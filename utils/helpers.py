import logging
import os
import random
import string
from pathlib import Path

import boto3
from PIL import Image
from boto3 import s3
from botocore.exceptions import ClientError
from fastapi import UploadFile


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# process upload image
def resize_image_file(file: UploadFile, store_file_dir_path: str, threshold=512):
    img = Image.open(file.file)
    img.thumbnail((threshold, threshold), Image.ANTIALIAS)
    img.save(Path(store_file_dir_path + file.filename))
