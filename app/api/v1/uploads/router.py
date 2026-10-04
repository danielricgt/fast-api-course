from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix='/upload', tags=['uploads'])
@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)): # three dots means its a required param
    return {
        "filename": "file uploaded",
        "file_size": len(file)
    }

@router.post("/file")
async def upload_file(file: UploadFile  = File(...) ):
    return  {
        "filename": file.filename,
        "content_type": file.content_type
    }
    