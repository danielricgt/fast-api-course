import asyncio
import shutil  # this allow me to manipulate system files
import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.file_storage import save_uploaded_image

router = APIRouter(prefix='/upload', tags=['uploads'])

MEDIA_DIR = "app/media"


@router.post("/bytes")
# three dots means its a required param
async def upload_bytes(file: bytes = File(...)):
    return {
        "filename": "file uploaded",
        "file_size": len(file)
    }


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    saved = save_uploaded_image(file)

    return {
        "filename": saved["filename"],
        "content_type": saved["content_type"],
        "url": saved["url"],
    }
