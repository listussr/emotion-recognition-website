from typing import Literal
from fastapi import APIRouter, UploadFile, HTTPException
from celery.exceptions import TimeoutError as CeleryTimeoutError

from worker.tasks import process_image
from app.schemas.responses import PhotoResponse
from app.config import settings

router = APIRouter()

@router.post("/", response_model=PhotoResponse)
async def handle_photo(file: UploadFile, model: Literal['convnext', 'swin', 'se_resnet'] = 'convnext'):
    """
    Эндпоинт для обработки фотографий.
    ---

    Args:
        file (UploadFile): Файл изображения.
        model (Literal[&#39;convnext&#39;, &#39;swin&#39;, &#39;se_resnet&#39;], optional): Название модели. Defaults to 'convnext'.

    Raises:
        HTTPException: Ошибка формата - stauts=415.
        HTTPException: Слишком тяжёлый файл - status=413.
        HTTPException: Превышение времени ожидания - status=504.
        HTTPException: Ошибка обработки - status=504.

    Returns:
        _type_: _description_
    """
    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.allowed_photo_formats:
        raise HTTPException(
            status_code=415,
            detail=f"Неподдерживаемый формат. Допустимые: {settings.allowed_photo_formats}"
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимум: {settings.max_file_size_mb} МБ"
        )

    try:
        task = process_image.delay(file_bytes, model)
        result = task.get(timeout=30)
    except CeleryTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Превышено время обработки. Попробуйте снова."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки: {str(e)}"
        )
    return result
