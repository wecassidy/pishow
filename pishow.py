import imghdr
import time
import os

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_foreign("cairo")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk
import cairo

IMG_DIR = "/home/wec/Pictures"
IMG_POLL_RATE = 1 # minute

DWELL_TIME = 10 # seconds
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
        self.current_image = next(self.images)
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
            self.current_image = next(self.images)
            self.last_switch = now

        size = self.get_allocation()

        try:
            img = GdkPixbuf.Pixbuf.new_from_file_at_size(
                self.current_image,
                size.width,
                size.height
            )
            Gdk.cairo_set_source_pixbuf(cr, img, 5, 5)
            cr.paint()
        except gi.repository.GLib.GError:
            self.current_image = next(self.images)

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
