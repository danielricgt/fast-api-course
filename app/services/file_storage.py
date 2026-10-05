# only takes the task to save a file in disk
import asyncio
import os
import shutil  # this allow me to manipulate system files
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status


MEDIA_DIR = "app/media"
ALLOW_MINE = ["image/png", "image/jpeg"]

# async def upload_bytes(file: bytes = File(...)): # three dots means its a required param
#     return {
#         "filename": "file uploaded",
#         "file_size": len(file)
#     }

# async def upload_file(file: UploadFile  = File(...) ):
#        return  {
#         "filename": file.filename,
#         "content_type": file.content_type
#     }


def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)

def save_uploaded_image(file: UploadFile) -> dict:
    if file.content_type not in ALLOW_MINE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="not allowed file type")
    ensure_media_dir()
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
    }
