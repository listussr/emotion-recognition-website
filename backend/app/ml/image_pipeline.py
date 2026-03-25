import time
import numpy as np
from typing import Literal
from .emotion_classifier import EmotionRecognizer
from .face_detector import FaceDetector
from .filters import fast_face_filter, pass_face_filters
from app.config import settings

_EMOTION_LABELS = ('anger', 'contempt', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise')

class ImageRecognizerPipeline(object):
    """
    Пайплайн обработки изображения.
    ---

    Публичные метод:
     - predict(image, model['опционально']) - предсказание эмоции выбранной моделью по изображению.
    """
    def __init__(self):
        self._detector = FaceDetector(min_detection_confidence=settings.detection_confidence)
        self._classifiers = {
            'convnext':  EmotionRecognizer(settings.model_path_convnext),
            'swin':      EmotionRecognizer(settings.model_path_swin),
            'se_resnet': EmotionRecognizer(settings.model_path_se_resnet),
        }

    def _idx_to_label(self, idx: int) -> str:
        """
        Перевод индекса эмоции в название.
        ---
        """
        if idx < 0 or idx >= len(_EMOTION_LABELS):
            return ""
        return _EMOTION_LABELS[idx]

    def predict(self, image: np.ndarray, model: Literal['convnext', 'se_resnet', 'swin'] = 'convnext',
                use_fast_filter: bool = True, use_pass_pace_filter: bool = True) -> dict:
        """
        Предсказание эмоций на лицах.
        ---

        Args:
            image (np.ndarray): Изображение для анализа.
            model (Literal[&#39;convnext&#39;, &#39;se_resnet&#39;, &#39;swin&#39;], optional): Название модели. Defaults to 'convnext'.

        Returns:
            dict: Словарь с данными о лицах, из эмоциях и аннотированное изображение.
        """
        start = time.time()

        detections = self._detector.detect(image, use_fast_filter, use_pass_pace_filter)
        faces = [
            image[y1:y1 + height, x1:x1 + width]
            for (x1, y1, width, height, _) in detections
        ]
        if not faces:
            return {
                'faces_num': 0,
                'process_time': round(time.time() - start, 3),
                'emotions': {},
            }, detections

        emotions = {}

        all_probs = self._classifiers[model].predict(faces)
        for i, probs in enumerate(all_probs):
            prob_dict = dict(zip(_EMOTION_LABELS, probs.tolist()))
            label = max(prob_dict, key=prob_dict.get)
            emotions[f'face_{i}'] = {
                'label': label,
                'is_detected': True,
                'probabilities': prob_dict,
            }

        return {
            'faces_num': len(faces),
            'process_time': round(time.time() - start, 3),
            'emotions': emotions,
        }, detections

pipeline_image = ImageRecognizerPipeline()
