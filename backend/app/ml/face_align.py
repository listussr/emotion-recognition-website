"""
Выравнивание лиц и оценка качества позы.
---

Используется для подготовки кропов под эмбеддер ArcFace (w600k_mbf) и
для фильтрации эмбеддингов низкого качества перед добавлением в трек.

Детектор MediaPipe BlazeFace (short-range) возвращает 6 ключевых точек:
    0: правый глаз
    1: левый глаз
    2: кончик носа
    3: центр рта
    4: козелок правого уха
    5: козелок левого уха

Для выравнивания под стандартный 5-точечный шаблон ArcFace (правый глаз,
левый глаз, нос, правый угол рта, левый угол рта) используется
упрощённая схема: центр рта заменяет оба угла рта (их нет у BlazeFace).
"""
from typing import List, Tuple, Optional

import cv2
import numpy as np


# Стандартный 5-точечный шаблон ArcFace для выходного размера 112x112.
# Порядок: правый глаз, левый глаз, нос, правый угол рта, левый угол рта.
ARCFACE_DST_5 = np.array([
    [38.2946, 51.6963],
    [73.5318, 51.5014],
    [56.0252, 71.7366],
    [41.5493, 92.3655],
    [70.7299, 92.2041],
], dtype=np.float32)

# Приведённый 4-точечный шаблон: eyes + nose + midpoint(mouth_corners).
_MOUTH_MID = (ARCFACE_DST_5[3] + ARCFACE_DST_5[4]) / 2.0
ARCFACE_DST_4 = np.stack([
    ARCFACE_DST_5[0],
    ARCFACE_DST_5[1],
    ARCFACE_DST_5[2],
    _MOUTH_MID,
], axis=0).astype(np.float32)

ARCFACE_SIZE = 112

Keypoints = List[Tuple[float, float]]


def align_face(image: np.ndarray, kps6: Keypoints) -> Optional[np.ndarray]:
    """
    Аффинное выравнивание лица к шаблону ArcFace (112x112).
    ---

    Args:
        image (np.ndarray): Исходный кадр BGR.
        kps6 (Keypoints): 6 ключевых точек в пиксельных координатах исходного кадра.

    Returns:
        Optional[np.ndarray]: Выровненный кроп 112x112 BGR, или None если landmarks невалидны.
    """
    if kps6 is None or len(kps6) < 4:
        return None

    right_eye = kps6[0]
    left_eye  = kps6[1]
    nose      = kps6[2]
    mouth_c   = kps6[3]

    src = np.array([right_eye, left_eye, nose, mouth_c], dtype=np.float32)

    if not np.all(np.isfinite(src)):
        return None

    M, _ = cv2.estimateAffinePartial2D(src, ARCFACE_DST_4, method=cv2.LMEDS)
    if M is None:
        return None

    aligned = cv2.warpAffine(
        image, M, (ARCFACE_SIZE, ARCFACE_SIZE),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0
    )
    return aligned


def pose_quality(
    kps6: Keypoints,
    bbox_wh: Tuple[float, float],
    yaw_max: float = 0.25,
    roll_max_deg: float = 20.0,
    min_face_px: int = 60,
) -> Tuple[bool, float]:
    """
    Быстрая оценка качества позы по landmarks.
    ---

    Приближение:
     * Yaw: горизонтальный сдвиг носа относительно середины глаз, нормированный на расстояние между глазами.
     * Roll: угол между линией глаз и горизонталью.
     * Size: минимальная сторона bbox.

    Args:
        kps6 (Keypoints): 6 ключевых точек.
        bbox_wh (Tuple[float, float]): (ширина, высота) bbox детекции.
        yaw_max (float): Максимальная доля смещения носа для прохождения фильтра.
        roll_max_deg (float): Максимальный угол наклона головы в градусах.
        min_face_px (int): Минимальная сторона bbox.

    Returns:
        Tuple[bool, float]:
            * bool — прошла ли детекция фильтр.
            * float — непрерывный скор в диапазоне [0, 1] для отладки/логирования.
    """
    if kps6 is None or len(kps6) < 4:
        return False, 0.0

    re = np.asarray(kps6[0], dtype=np.float32)
    le = np.asarray(kps6[1], dtype=np.float32)
    nose = np.asarray(kps6[2], dtype=np.float32)

    eye_mid = (re + le) / 2.0
    eye_dist = float(np.linalg.norm(le - re))
    if eye_dist < 1e-3:
        return False, 0.0

    yaw_ratio = float(abs(nose[0] - eye_mid[0]) / eye_dist)
    roll_deg = float(abs(np.degrees(np.arctan2(le[1] - re[1], le[0] - re[0]))))

    w, h = bbox_wh
    size_ok = min(w, h) >= min_face_px

    good = (yaw_ratio < yaw_max) and (roll_deg < roll_max_deg) and size_ok
    score = max(0.0, 1.0 - min(yaw_ratio / max(yaw_max, 1e-6), 1.0))
    return good, score
