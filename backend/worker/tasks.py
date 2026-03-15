import base64
import numpy as np
import cv2

from app.services.queue import celery_app
from app.ml import ImageRecognizerPipeline
from app.ml.visualizer import annotate

image_recognizer = ImageRecognizerPipeline()

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

    result, detections = image_recognizer.predict(image, model)
    image_bytes = annotate(image, detections, result['emotions'])
    result['result_image'] = base64.b64encode(image_bytes).decode('utf-8')

    return result