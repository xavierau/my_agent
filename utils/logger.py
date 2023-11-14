import json
from datetime import datetime

from pydantic import BaseModel


class Logger(BaseModel):

    @classmethod
    def info(cls, message: str, data: dict = None):
        file = open("tools.log", "a")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = " ".join([f"INFO: {timestamp}:", message, "\n"])
        file.write(msg)
        file.close()

    @classmethod
    def debug(cls, message: str, data: dict = None):
        file = open("tools.log", "a")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = " ".join([f"DEBUG: {timestamp}:", message, "\n"])
        file.write(msg)
        file.close()

    @classmethod
    def warning(cls, message: str, data: dict = None):
        file = open("tools.log", "a")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = " ".join([f"WARNING: {timestamp}:", message, "\n"])
        file.write(msg)
        file.close()
