import os

IMG_DIR = "./img/"
IMG_POLL_RATE = 1 # minute

def get_files_recursive(root_dir):
    """Yield an iterator of file paths in root_dir."""
    for directory in os.walk(root_dir):
        for file in directory[2]:
            yield os.path.join(directory[0], file)

image_list = get_files_recursive(IMG_DIR)
for image in image_list:
    print(image)
