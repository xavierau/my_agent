import os
import random
import string
from urllib.parse import urlparse
from os.path import exists

from PIL import Image
from fastapi import UploadFile


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# process upload image
def resize_image_file(file: UploadFile, store_file_dir_path: str, threshold=512):
    img = Image.open(file.file)
    img.thumbnail((threshold, threshold), Image.ANTIALIAS)
    path = os.path.join(store_file_dir_path, file.filename)
    img.save(path)


def is_local(url):
    url_parsed = urlparse(url)
    if url_parsed.scheme in ('file', ''):  # Possibly a local file
        return exists(url_parsed.path)
    return False
