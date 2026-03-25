import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import List, Tuple
import logging
from .filters import fast_face_filter, pass_face_filters

class FaceDetector:
    """
    Детектор лиц на основе MediaPipe.
    ---
    """
    def __init__(self, model_path: str = 'app/ml/models/blaze_face_short_range.tflite', min_detection_confidence: float = 0.7):
        """
        Детектор лиц на основе MediaPipe.
        ---

        Args:
            model_path (str, optional): Путь к модели MediaPipe. Defaults to 'app/ml/models/blaze_face_short_range.tflite'.
            min_detection_confidence (float, optional): Порог уверенности для признания детекции лицом. Defaults to 0.7.
        """
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence,
        )
        self._detector = vision.FaceDetector.create_from_options(options)

        dummy = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=np.zeros((128, 128, 3), dtype=np.uint8)
        )
        for _ in range(3):
            self._detector.detect(dummy)

    def _geometry_post_filters(self, height: int, width: int, frame_height: int, frame_width: int) -> bool:
        """
        Базовые геометрические фильтры для детекций.
        ---
        """
        ratio = height / max(width, 1)
        area = width * height
        frame_area = frame_width * frame_height
        return not any([
            width <= 0 or height <= 0,
            width < 40 or height < 40,
            ratio < 0.75 or ratio > 1.7,
            area < 0.002 * frame_area or area > 0.5 * frame_area,
        ])

    def detect(self, image: np.ndarray, use_fast_filter: bool = False, use_pass_pace_filter: bool = False) -> List[Tuple[int, int, int, int, float]]:
        """
        Детекция лиц.
        ---

        Args:
            image (np.ndarray): Изображение для детекции.

        Returns:
            List[Tuple[int, int, int, int, float]]: Список координат лиц и уверенности детектора.
        """
        if image is None or image.size == 0:
            logging.warning("Face detector got empty image")
            return []

        orig_h, orig_w = image.shape[:2]

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )

        result = self._detector.detect(mp_image)
        detections = []

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        if not result.detections:
            return detections

        for detection in result.detections:
            bbox = detection.bounding_box
            conf = detection.categories[0].score

            x_min = max(0, bbox.origin_x)
            y_min = max(0, bbox.origin_y)
            width = min(orig_w - x_min, bbox.width)
            height = min(orig_h - y_min, bbox.height)

            if not self._geometry_post_filters(height, width, orig_h, orig_w):
                continue

            crop = gray[y_min:y_min + height, x_min:x_min + width]

            if use_fast_filter:
                if not fast_face_filter(crop, width, height):
                    continue

            if use_pass_pace_filter:
                if not pass_face_filters(crop, width, height):
                    continue

            detections.append((x_min, y_min, width, height, conf))

        return detections

    def __del__(self):
        if hasattr(self, '_detector'):
            self._detector.close()