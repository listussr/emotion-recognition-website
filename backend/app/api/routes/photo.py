from fastapi import APIRouter, UploadFile
from worker.tasks import process_image

router = APIRouter()

@router.post("/")
async def handle_photo(file: UploadFile):
    file_bytes = await file.read()

    task = process_image.delay(file_bytes)
    result = task.get(timeout=30)

    return result
