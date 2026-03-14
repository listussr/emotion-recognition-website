import time
from app.services.queue import celery_app

@celery_app.task
def process_image(data: bytes) -> dict:
    """
    Заглушка

    Args:
        data (bytes): _description_

    Returns:
        dict: _description_
    """
    try:
        time.sleep(2)
        return {
            "faces_num": 1,
            "process_time": 2.0,
            "emotions": {
                "face_0": {
                    "label": "happy",
                    "is_detected": True,
                    "probabilities": {"happy": 0.9, "sad": 0.1}
                }
            }
        }
    except Exception as e:
        return {"error": str(e), "faces_num": 0, "emotions": {}}