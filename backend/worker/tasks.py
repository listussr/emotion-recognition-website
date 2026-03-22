import base64
import numpy as np
import cv2
import traceback

from app.services.queue import celery_app
from app.ml import pipeline_image, pipeline_video
from app.ml.visualizer import annotate

@celery_app.task
def process_image(data: bytes, model: str = 'convnext') -> dict:
    """
    Задача классификации эмоций и аннотации изображения.
    ---

    Args:
        data (bytes): Входное изображение.
        model (str, optional): Название модели. Defaults to 'convnext'.

    Returns:
        dict: Словарь с аннотированным изображением и данными об эмоциях.
    """
    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return {
            'faces_num': 0,
            'process_time': 0.0,
            'emotions': {},
            'result_image': ''
        }

    result, detections = pipeline_image.predict(image, model)
    image_bytes = annotate(image, detections, result['emotions'])
    result['result_image'] = base64.b64encode(image_bytes).decode('utf-8')

    return result

@celery_app.task
def process_video(file_path: str, model: str = 'convnext') -> dict:
    """
    Задача классификации эмоций и аннотации изображения.
    ---

    Args:
        data (bytes): Входное видео.
        model (str, optional): Название модели. Defaults to 'convnext'.

    Returns:
        dict: Словарь с аннотированным видео и метаданными обработки.
    """
    
    try:
        return pipeline_video.process(file_path, model)
    except Exception as e:
        return {
            'processing_fps': 0.0,
            'duration_sec': 0.0,
            'total_frames_processed': 0,
            'result_video': '',
            'error': traceback.format_exc()
        }