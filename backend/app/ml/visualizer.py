import cv2
import numpy as np
from typing import Dict, List, Tuple

LEGEND_WIDTH = 220
FONT = cv2.FONT_HERSHEY_SIMPLEX
PADDING = 15
LINE_HEIGHT = 20

_COLORS = {
    'anger':    (0, 0, 255),
    'contempt': (128, 0, 128),
    'disgust':  (0, 128, 0),
    'fear':     (0, 128, 128),
    'happy':    (0, 255, 255),
    'neutral':  (128, 128, 128),
    'sad':      (255, 0, 0),
    'surprise': (0, 165, 255)
}

def draw_annotations(image: np.ndarray, detections: List[Tuple], emotions: Dict[str, Dict]) -> np.ndarray:
    """
    Отрисовка границ лиц и информации о наиболее явной эмоции.
    ---

    Args:
        image (np.ndarray): Исходное изображение.
        detections (List[Tuple]): Список детекций от детектора лиц.
        emotions (Dict[str, Dict]): Словарь с эмоциями для всех лиц.

    Returns:
        np.ndarray: Аннотированное изображение.
    """
    for i, detection in enumerate(detections):
        face_key = f'face_{i}'
        if face_key not in emotions:
            continue

        x1, y1, w, h, _ = detection
        x1, y1, x2, y2 = map(int, (x1, y1, x1 + w, y1 + h))

        emotion_data = emotions[face_key]
        emotion_label = emotion_data['label']
        emotion_prob = emotion_data['probabilities'][emotion_label]
        color = _COLORS.get(emotion_label, (255, 255, 255))

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        face_label = f'face_{i}'
        cv2.putText(image, face_label, (x1, y1 - 25), FONT, 0.55, color, 2, cv2.LINE_AA)

        emotion_text = f'{emotion_label}: {emotion_prob * 100:.1f}%'
        cv2.putText(image, emotion_text, (x1, y1 - 8), FONT, 0.5, color, 1, cv2.LINE_AA)

    return image


def draw_legend(height: int, emotions: Dict[str, Dict]) -> np.ndarray:
    """
    Отрисовка легенды для изображения.
    ---

    Args:
        height (int): Высота изображения.
        emotions (Dict[str, Dict]): Словарь эмоций для каждого лица.

    Returns:
        np.ndarray: Изображение легенды.
    """
    legend = np.zeros((height, LEGEND_WIDTH, 3), dtype=np.uint8)

    cv2.putText(legend, 'Faces', (PADDING, PADDING + LINE_HEIGHT),
                FONT, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.line(legend, (PADDING, PADDING + LINE_HEIGHT + 5),
             (LEGEND_WIDTH - PADDING, PADDING + LINE_HEIGHT + 5),
             (80, 80, 80), 1)

    y_offset = PADDING + LINE_HEIGHT * 2 + 10

    for face_key, emotion_data in emotions.items():
        if y_offset + LINE_HEIGHT * 3 > height:
            break

        emotion_label = emotion_data['label']
        emotion_prob = emotion_data['probabilities'][emotion_label]
        color = _COLORS.get(emotion_label, (255, 255, 255))

        cv2.rectangle(legend,
                      (PADDING, y_offset - 12),
                      (PADDING + 12, y_offset),
                      color, -1)
        cv2.putText(legend, face_key, (PADDING + 18, y_offset),
                    FONT, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        y_offset += LINE_HEIGHT

        emotion_text = f'{emotion_label}: {emotion_prob * 100:.1f}%'
        cv2.putText(legend, emotion_text, (PADDING, y_offset),
                    FONT, 0.45, color, 1, cv2.LINE_AA)

        y_offset += LINE_HEIGHT + 8

        cv2.line(legend,
                 (PADDING, y_offset),
                 (LEGEND_WIDTH - PADDING, y_offset),
                 (50, 50, 50), 1)

        y_offset += 8

    return legend


def annotate(image: np.ndarray, detections: List[Tuple], emotions: Dict[str, Dict]) -> bytes:
    """
    Аннотирование изображения и отрисовка легенды.
    ---

    Происходит в 3 этапа:
     1) Аннотирование лиц на картинке.
     2) Отрисовка легенды.
     3) Совмещение легенды и картинки.

    Args:
        image (np.ndarray): Исходное изображение.
        detections (List[Tuple]): Список детекций.
        emotions (Dict[str, Dict]): Словарь эмоций для каждого лица.

    Returns:
        bytes: Финальная версия изображения с легендой.
    """
    if not detections or not emotions:
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()

    annotated = draw_annotations(image.copy(), detections, emotions)
    legend = draw_legend(image.shape[0], emotions)
    combined = np.hstack([annotated, legend])
    _, buffer = cv2.imencode('.jpg', combined, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return buffer.tobytes()
