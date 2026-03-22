import numpy as np
from typing import Dict, List, Tuple
from itertools import product

# x, y, width, height
CoordsXYWH = Tuple[float, float, float, float]
# x1, y1, x2, y2
CoordsLTRB = Tuple[float, float, float, float]

def xywh_to_ltrb(boxA: CoordsXYWH) -> CoordsLTRB:
    return boxA[0], boxA[1], boxA[0] + boxA[2], boxA[1] + boxA[3]

def ltrb_to_xywh(boxA: CoordsLTRB) -> CoordsXYWH:
    return boxA[0], boxA[1], boxA[2] - boxA[0], boxA[3] - boxA[1]

def IoU(boxA: CoordsXYWH, boxB: CoordsXYWH) -> float:
    """
    IoU-метрика.
    ---

    Args:
        boxA (CoordsXYWH): Границы объекта на первом кадре.
        boxB (CoordsXYWH): Границы объекта на втором кадре.

    Returns:
        float: Значение метрики.
    """
    x1_1, y1_1, x1_2, y1_2 = xywh_to_ltrb(boxA)
    x2_1, y2_1, x2_2, y2_2 = xywh_to_ltrb(boxB)
    x_left = max(x1_1, x2_1)
    y_top = max(y1_1, y2_1)
    x_right = min(x1_2, x2_2)
    y_bottom = min(y1_2, y2_2)
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    area_A = (x1_2 - x1_1) * (y1_2 - y1_1)
    area_B = (x2_2 - x2_1) * (y2_2 - y2_1)
    union_area = area_A + area_B - intersection_area
    return intersection_area / union_area

class Track:
    __slots__ = ('id', 'bbox', 'velocity', 'age', 'emotion')

    def __init__(
            self,
            track_id: int,
            bbox: CoordsXYWH,
            velocity: CoordsXYWH = (0.0, 0.0, 0.0, 0.0),
            age: int = 0,
            emotion: dict = None
        ):
        """
        Трек лица.
        ---

        Args:
            track_id (int): Идентификатор трека.
            bbox (CoordsXYWH): Границы лица.
            velocity (CoordsXYWH, optional): Скорость изменения координат. Defaults to (0.0, 0.0, 0.0, 0.0).
            age (int, optional): Возраст трека. Defaults to 0.
            emotion (dict, optional): Данные об эмоциях лица. Defaults to None.
        """
        self.id = track_id
        self.bbox = bbox
        self.velocity = velocity
        self.age = age
        self.emotion = emotion or {}

    def move(self) -> CoordsXYWH:
        return (
            self.bbox[0] + self.velocity[0],
            self.bbox[1] + self.velocity[1],
            self.bbox[2] + self.velocity[2],
            self.bbox[3] + self.velocity[3],
        )

class Tracker:
    __slots__ = ('tracks', '_iou_threshold', '_track_ttl', '_next_id', '_step')

    def __init__(self, iou_threshold: float, track_ttl: int = 5, step: int = 1):
        self.tracks: List[Track] = []
        self._next_id = 0
        self._track_ttl = track_ttl
        self._iou_threshold = iou_threshold
        self._step = step

    def update(self, detections: List[CoordsXYWH], emotions: Dict[str, dict]):
        """
        Обновление реальных состояний треков.
        ---

        Args:
            detections (List[CoordsXYWH]): Список детекций от детектора.
            emotions (Dict[str, dict]): Словарь с данными эмоций для каждого лица.
        """
        if not detections:
            for track in self.tracks:
                track.age += 1
            self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
            return

        if not self.tracks:
            for i, bbox in enumerate(detections):
                emotion = emotions.get(f'face_{i}', {})
                self.tracks.append(Track(
                    track_id=self._next_id,
                    bbox=bbox,
                    emotion=emotion
                ))
                self._next_id += 1
            return

        iou_matrix = np.zeros((len(self.tracks), len(detections)), dtype=float)
        for t_idx, d_idx in product(range(len(self.tracks)), range(len(detections))):
            iou_matrix[t_idx, d_idx] = IoU(self.tracks[t_idx].bbox, detections[d_idx])

        matched_tracks = set()
        matched_detections = set()

        while True:
            t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            if iou_matrix[t_idx, d_idx] < self._iou_threshold:
                break

            track = self.tracks[t_idx]
            new_bbox = detections[d_idx]
            track.velocity = (
                (new_bbox[0] - track.bbox[0]) / self._step,
                (new_bbox[1] - track.bbox[1]) / self._step,
                (new_bbox[2] - track.bbox[2]) / self._step,
                (new_bbox[3] - track.bbox[3]) / self._step,
            )
            track.bbox = new_bbox
            track.age = 0
            track.emotion = emotions.get(f'face_{d_idx}', track.emotion)

            matched_tracks.add(t_idx)
            matched_detections.add(d_idx)

            iou_matrix[t_idx, :] = -1
            iou_matrix[:, d_idx] = -1

        for d_idx, bbox in enumerate(detections):
            if d_idx not in matched_detections:
                emotion = emotions.get(f'face_{d_idx}', {})
                self.tracks.append(Track(
                    track_id=self._next_id,
                    bbox=bbox,
                    emotion=emotion
                ))
                self._next_id += 1

        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.age += 1

        self.tracks = [t for t in self.tracks if t.age < self._track_ttl]

    def predict(self):
        """
        Обновление треков путём предсказания движения.
        ---
        """
        self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
        for track in self.tracks:
            track.bbox = track.move()
            track.age += 1

    def get_tracks(self) -> List[Track]:
        """
        Получение состояний треков.
        ---

        Returns:
            List[Track]: Состояния текущих треков.
        """
        return self.tracks
