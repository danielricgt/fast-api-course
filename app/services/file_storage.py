# only takes the task to save a file in disk
import asyncio
import os
import shutil  # this allow me to manipulate system files
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status


MEDIA_DIR = "app/media"
ALLOW_MINE = ["image/png", "image/jpeg"]
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "3"))
CHUNKS = 1024 * 1024

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



    class _ChunkCounter:
        def __init__(self, f):
            self._f = f
            self.calls = 0
            self.sizes = []
        def read(self, n=-1):
            data = self._f.read(n)
            if data:
                self.calls += 1
                self.sizes.append(len(data))
            return data
        def __getattr__(self, name):  # delega cualquier otro atributo
            return getattr(self._f, name)

    reader = _ChunkCounter(file.file)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(reader, buffer, length=CHUNKS)
        
    size = os.path.getsize(file_path)
    if size > MAX_MB * CHUNKS :
        os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE, 
                            detail=f"the file exceeds size limit > {MAX_MB} MB" )

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
        "size": size,
        "chunk_size_used": CHUNKS,
        "chunk_calls": reader.calls,
        "chunks_sizes_sample": reader.sizes[:5]
    }
