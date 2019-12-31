import imghdr
import time
import os

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_foreign("cairo")
from gi.repository import GLib, Gtk
import cairo

import PIL.Image as Image

IMG_DIR = "/home/wec/Pictures"
IMG_POLL_RATE = 1 # minute

DWELL_TIME = 5 # seconds
FADE_TIME = 1 # seconds

REFRESH_RATE = 10 # milliseconds

def get_files_recursive(root_dir):
    """Yield an iterator of file paths in root_dir."""
    for directory in os.walk(root_dir):
        for file in directory[2]:
            yield os.path.join(directory[0], file)

class Slideshow(Gtk.DrawingArea):
    def __init__(self, image_source, dwell, refresh_rate=REFRESH_RATE):
        """Set up the slideshow.

        @param image_source: a non-empty iterable of path-like objects
            pointing to images.

        @param dwell: how long to linger on each image, in seconds.

        @param refresh_rate: how frequently to refresh the image on
            screen, in milliseconds.
        """
        Gtk.DrawingArea.__init__(self)

        self.connect("draw", self.slideshow)

        self.images = iter(image_source)
        self.last_image = None
        self.current_image = SlideImage(next(self.images))
        self.last_switch = time.time()

        self.dwell = dwell
        self.refresh_rate = refresh_rate

        # Start the slideshow: trigger redraw every refresh_rate ms
        GLib.timeout_add(self.refresh_rate, self.ticker)

    def ticker(self):
        """Force a draw event to fire whenever the program ticks"""
        rect = self.get_allocation()
        self.get_window().invalidate_rect(rect, True)
        return True # Keep the animation ticking

    def slideshow(self, widget, cr):
        """Run the slideshow"""
        now = time.time()
        if now - self.last_switch > self.dwell:
            self.switch_images()
            self.last_switch = now

        self.current_image.fade_in(self.last_switch)

        for img in self.last_image, self.current_image:
            if img is not None:
                surface = img.surface()
                size = self.get_allocation()
                scale = self.scale_to_fit(surface)
                translation = self.centre(surface, scale)

                # Black background
                cr.set_source_rgba(0, 0, 0, img.alpha)
                cr.rectangle(0, 0, size.width, size.height)
                cr.fill()

                # Image
                cr.save()
                cr.translate(*translation)
                cr.scale(scale, scale)
                cr.set_source_surface(surface, 0, 0)
                cr.paint_with_alpha(img.alpha)
                cr.restore()

    def scale_to_fit(self, surface):
        """
        Calculate the scaling for a given surface to fit it the
        container, preserving aspect ratio.

        Based on https://stackoverflow.com/q/7145780/3311667.
        """
        size = self.get_allocation()
        width_ratio = float(size.width) / float(surface.get_width())
        height_ratio = float(size.height) / float(surface.get_height())
        scale_xy = min(height_ratio, width_ratio)
        return scale_xy

    def centre(self, surface, scale):
        """
        Calculate the (x, y) coordinates of the top left corner of the
        given surface to centre it on the container.
        """
        size = self.get_allocation()
        x = (size.width - surface.get_width() * scale) / 2
        y = (size.height - surface.get_height() * scale) / 2
        return x, y

    def switch_images(self):
        next_image = None
        while next_image is None:
            try:
                next_image = SlideImage(next(self.images))
            except FileNotFoundError:
                pass
        self.last_image = self.current_image
        self.current_image = next_image

class SlideImage:
    """An animated image in the slideshow"""
    def __init__(self, filename, x=0, y=0, zoom=1, alpha=1):
        self.filename = filename
        self.image = Image.open(filename)
        self.pos = (x, y)
        self.zoom = zoom
        self.alpha = alpha

    def surface(self):
        """
        Convert the image to a Cairo surface. Copied from
        https://pycairo.readthedocs.io/en/latest/integration.html#pillow-pil-cairo
        """
        self.image.putalpha(256)
        arr = bytearray(self.image.tobytes('raw', 'BGRa'))
        surface = cairo.ImageSurface.create_for_data(
            arr,
            cairo.Format.ARGB32,
            self.image.width,
            self.image.height
        )
        return surface

    def fade_in(self, start, fade_time=FADE_TIME):
        self.alpha = min((time.time() - start) / fade_time, 1)

if __name__ == "__main__":
    # Set up drawing area
    window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit)
    window.maximize()

    files = get_files_recursive(IMG_DIR)
    images = filter(lambda f: imghdr.what(f) is not None, files)

    slides = Slideshow(images, DWELL_TIME)
    window.add(slides)

    window.show_all()
    Gtk.main()
