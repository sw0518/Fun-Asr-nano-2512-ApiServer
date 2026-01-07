import os
import tempfile
from typing import BinaryIO

def save_upload_file_tmp(upload_file: BinaryIO) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(upload_file.read())
            return tmp.name
    except Exception as e:
        raise e

def cleanup_tmp_file(path: str):
    if os.path.exists(path):
        os.remove(path)
