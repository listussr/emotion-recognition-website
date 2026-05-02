import time
import numpy as np
from typing import Dict, Literal, Optional
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
        self._classifier_specs = {
            'convnext':        (settings.model_path_convnext,        settings.model_input_size_convnext),
            'swin':            (settings.model_path_swin,            settings.model_input_size_swin),
            'resnet_50':       (settings.model_path_resnet_50,       settings.model_input_size_resnet_50),
            'efficientnet_b3': (settings.model_path_efficientnet_b3, settings.model_input_size_efficientnet_b3),
        }
        self._classifiers: dict[str, EmotionRecognizer] = {}

    def _get_classifier(self, model: str) -> EmotionRecognizer:
        """Ленивая инициализация ORT-сессии под запрошенную модель."""
        clf = self._classifiers.get(model)
        if clf is None:
            path, input_size = self._classifier_specs[model]
            clf = EmotionRecognizer(path, input_size)
            self._classifiers[model] = clf
        return clf

    def _idx_to_label(self, idx: int) -> str:
        """
        Перевод индекса эмоции в название.
        ---
        """
        if idx < 0 or idx >= len(_EMOTION_LABELS):
            return ""
        return _EMOTION_LABELS[idx]

    def predict(self, image: np.ndarray,
                model: Literal['convnext', 'swin', 'resnet_50', 'efficientnet_b3'] = 'convnext',
                use_fast_filter: bool = True, use_pass_pace_filter: bool = True,
                prof: Optional[Dict[str, float]] = None) -> dict:
        """
        Предсказание эмоций на лицах.
        ---

        Args:
            image (np.ndarray): Изображение для анализа.
            model (Literal[&#39;convnext&#39;, &#39;swin&#39;, &#39;resnet_50&#39;, &#39;efficientnet_b3&#39;], optional): Название модели. Defaults to 'convnext'.

        Returns:
            dict: Словарь с данными о лицах, из эмоциях и аннотированное изображение.
        """
        start = time.time()

        t0 = time.perf_counter() if prof is not None else 0.0
        detections = self._detector.detect(image, use_fast_filter, use_pass_pace_filter)
        if prof is not None:
            prof['detect'] += time.perf_counter() - t0
        faces = [
            image[y1:y1 + height, x1:x1 + width]
            for (x1, y1, width, height, *_) in detections
        ]
        if not faces:
            return {
                'faces_num': 0,
                'process_time': round(time.time() - start, 3),
                'emotions': {},
            }, detections

        emotions = {}

        t0 = time.perf_counter() if prof is not None else 0.0
        all_probs = self._get_classifier(model).predict(faces)
        if prof is not None:
            prof['emotion'] += time.perf_counter() - t0
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
