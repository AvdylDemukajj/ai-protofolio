import os
import uuid
from backend.config import settings

def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """Saves file and returns path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path