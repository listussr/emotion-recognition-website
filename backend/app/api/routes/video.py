import tempfile
import os
from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/")
async def handle_video(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        import time
        time.sleep(10)
    finally:
        os.remove(tmp_path)

    return None