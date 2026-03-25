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

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Мера косинусного сходства 2 эмбеддингов.
    ---

    Args:
        a (np.ndarray): Первый эмбеддинг.
        b (np.ndarray): Второй эмбеддинг.

    Returns:
        float: Косинусное сходство.
    """
    a = a.flatten()
    b = b.flatten()

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:
        return -1.0

    return float(np.dot(a, b) / (a_norm * b_norm))

class Track:
    __slots__ = ('id', 'bbox', 'velocity', 'age', 'emotion', 'history', 'embedding', 'identity_threshold', 'hits', 'confirmed')

    def __init__(
            self,
            track_id: int,
            bbox: CoordsXYWH,
            velocity: CoordsXYWH = (0.0, 0.0, 0.0, 0.0),
            age: int = 0,
            emotion: Dict = None,
            history: List[Dict] = None,
            embedding: np.ndarray = None,
            identity_threshold: float = 0.5
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
        self.history = history or []
        self.embedding = embedding if embedding is not None else np.zeros(512, dtype=np.float32)
        self.identity_threshold = identity_threshold
        self.hits = 1
        self.confirmed = False

    def move(self) -> CoordsXYWH:
        """
        Смещение координат трека.
        ---

        Returns:
            CoordsXYWH: Новые координаты.
        """
        return (
            self.bbox[0] + self.velocity[0],
            self.bbox[1] + self.velocity[1],
            self.bbox[2] + self.velocity[2],
            self.bbox[3] + self.velocity[3],
        )

    def check_identity(self, embedding: np.ndarray) -> bool:
        """
        Проверка принадлежности лица конкретному треку.
        ---

        Возвращаемые значения:
         * True - Лицо принадлежит треку / трек новый.
         * False - Лицо не соответствует этому треку. 

        Args:
            embedding (np.ndarray): Эмбеддинги сравниваемого лица.

        Returns:
            bool: Приндлежность лица данному треку.
        """
        if self.embedding is None or np.all(self.embedding == 0):
            return True

        similarity = cosine_similarity(self.embedding, embedding)
        return similarity >= self.identity_threshold

class Tracker:
    __slots__ = ('tracks', '_iou_threshold', '_track_ttl', '_next_id', '_step', '_reid_threshold', '_confirmation_threshold')

    def __init__(self, iou_threshold: float, track_ttl: int = 5, step: int = 1, reid_threshold: float = 0.55, confirmation_threshold: int = 5):
        """
        Трекер лиц в видеопотоке.
        ---

        Базируется на IoU метрике и на реидентификации лиц.

        Args:
            iou_threshold (float): Порог метрики IoU для признания лица тем же треком.
            track_ttl (int, optional): Время жизни трека. Defaults to 5.
            step (int, optional): Частота вызова обноовления треков - для корректной скорости отображения границ лиц. Defaults to 1.
            reid_threshold (float, optional): Минимальный порог схожести лиц при реидентификации. Defaults to 0.55.
            confirmation_threshold (int, optional): Минимальное количество обновлений для признания трека действующим. Defaults to 5.
        """
        self.tracks: List[Track] = []
        self._next_id = 0
        self._track_ttl = track_ttl
        self._iou_threshold = iou_threshold
        self._step = step
        self._reid_threshold = reid_threshold
        self._confirmation_threshold = confirmation_threshold

    def update(self, detections: List[CoordsXYWH], emotions: Dict[str, dict], embeddings: np.ndarray, timestamp: float = 0.0):
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
                emb = embeddings[i] if len(embeddings) > i else np.zeros(512, dtype=np.float32)
                track = Track(track_id=self._next_id, bbox=bbox, emotion=emotion, embedding=emb)
                track.history.append({'timestamp': timestamp, 'emotion': emotion})
                self.tracks.append(track)
                self._next_id += 1
            return

        iou_matrix = np.zeros((len(self.tracks), len(detections)), dtype=float)
        for t_idx, d_idx in product(range(len(self.tracks)), range(len(detections))):
            iou_matrix[t_idx, d_idx] = IoU(self.tracks[t_idx].bbox, detections[d_idx])

        matched_tracks = set()
        matched_detections = set()

        while True:
            if np.max(iou_matrix) < self._iou_threshold:
                break

            t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)

            track = self.tracks[t_idx]
            new_emb = embeddings[d_idx] if len(embeddings) > d_idx else None

            if new_emb is not None and not track.check_identity(new_emb):
                iou_matrix[t_idx, d_idx] = -1
                continue

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

            if new_emb is not None:
                track.embedding = 0.9 * track.embedding + 0.1 * new_emb
                track.embedding /= (np.linalg.norm(track.embedding) + 1e-6)

            track.history.append({'timestamp': timestamp, 'emotion': track.emotion})

            track.hits += 1

            if track.hits >= self._confirmation_threshold:
                track.confirmed = True

            matched_tracks.add(t_idx)
            matched_detections.add(d_idx)

            iou_matrix[t_idx, :] = -1
            iou_matrix[:, d_idx] = -1

        for d_idx, bbox in enumerate(detections):
            if d_idx in matched_detections:
                continue

            emb = embeddings[d_idx] if len(embeddings) > d_idx else None

            best_track = None
            best_similarity = -1

            if emb is not None:
                for t_idx, track in enumerate(self.tracks):

                    if t_idx in matched_tracks:
                        continue

                    similarity = cosine_similarity(track.embedding, emb)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_track = track

            if best_track is not None and best_similarity >= self._reid_threshold:
                best_track.bbox = bbox
                best_track.age = 0
                best_track.emotion = emotions.get(f'face_{d_idx}', best_track.emotion)

                best_track.embedding = 0.9 * best_track.embedding + 0.1 * emb
                best_track.embedding /= (np.linalg.norm(best_track.embedding) + 1e-6)

                best_track.history.append({'timestamp': timestamp, 'emotion': best_track.emotion})

                track.hits += 1

                if track.hits >= self._confirmation_threshold:
                    track.confirmed = True
                
                matched_detections.add(d_idx)
                matched_tracks.add(self.tracks.index(best_track))

            else:
                emotion = emotions.get(f'face_{d_idx}', {})
                emb = embeddings[d_idx] if len(embeddings) > d_idx else np.zeros(512, dtype=np.float32)
                track = Track(track_id=self._next_id, bbox=bbox, emotion=emotion, embedding=emb)
                track.history.append({'timestamp': timestamp, 'emotion': emotion})
                self.tracks.append(track)
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
        return [t for t in self.tracks if t.confirmed]
