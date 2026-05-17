import os
import shutil
from backend.config import settings

def save_uploaded_file(file, filename: str) -> str:
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)
    return file_path