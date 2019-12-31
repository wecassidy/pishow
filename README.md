# PiShow
A slideshow designed to run on a Raspberry Pi (though it will run on
any computer with Gtk3+ and Pillow).

# Requirements
- Python 3
- Python 3 bindings for gobject-introspection libraries
- Python 3 cairo bindings
- Pillow

# Setup
1. Clone this repository
2. Install dependencies
3. Copy `config_default.py` to `config.py`
4. Set `IMG_DIR` in `config.py` to a directory containing the images
   for the slideshow
5. Run `pishow.py` to start the slideshow
