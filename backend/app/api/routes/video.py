import tempfile
import os
from typing import Literal
from fastapi import APIRouter, UploadFile, HTTPException
from celery.exceptions import TimeoutError as CeleryTimeoutError

from worker.tasks import process_video
from app.schemas.responses import VideoResponse
from app.config import settings

router = APIRouter()

@router.post("/", response_model=VideoResponse)
async def handle_video(file: UploadFile,
                       model: Literal['convnext', 'swin', 'resnet_50', 'efficientnet_b3'] = 'convnext'):
    """
    Эндпоинт для обработки видео.
    ---

    Args:
        file (UploadFile): Видео файл.
        model (Literal[&#39;convnext&#39;, &#39;swin&#39;, &#39;resnet_50&#39;, &#39;efficientnet_b3&#39;], optional): Название модели. Defaults to 'convnext'.

    Raises:
        HTTPException: Ошибка формата - status=415.
        HTTPException: Слишком тяжёлый файл - status=413.
        HTTPException: Превышение времени ожидания - status=504.
        HTTPException: Ошибка обработки - status=504.

    Returns:
        _type_: _description_
    """
    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.allowed_video_formats:
        raise HTTPException(
            status_code=415,
            detail=f"Неподдерживаемый формат. Допустимые: {settings.allowed_video_formats}"
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимум: {settings.max_file_size_mb} МБ"
        )

    # Write into a directory that is shared between backend and worker
    # containers (see SHARED_TMP_DIR in docker-compose). Without this the
    # worker cannot open the file — different containers don't share /tmp.
    tmp_path = None
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4",
        dir=settings.shared_tmp_dir,  # None → system tempdir
    ) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        task = process_video.delay(tmp_path, model)
        result = task.get(timeout=settings.video_processing_timeout)
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
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result
