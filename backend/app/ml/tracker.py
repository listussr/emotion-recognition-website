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
    __slots__ = (
        'id', 'bbox', 'image', 'velocity', 'age', 'emotion',
        'history', 'embeddings', 'identity_threshold', 'hits',
        'confirmed', 'gallery_age'
    )

    def __init__(
            self,
            track_id: int,
            bbox: CoordsXYWH,
            image: np.ndarray,
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
            identity_threshold (float, optional): Порог косинусного сходства для check_identity. Defaults to 0.5.
        """
        self.id = track_id
        self.bbox = bbox
        self.velocity = velocity
        self.age = age
        self.image = image
        self.emotion = emotion or {}
        self.history = history or []
        self.embeddings = [embedding] if embedding is not None else []
        self.identity_threshold = identity_threshold
        self.hits = 1
        self.confirmed = False
        self.gallery_age = 0

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
        if not self.embeddings:
            return True

        sims = [cosine_similarity(e, embedding) for e in self.embeddings]
        return max(sims) >= self.identity_threshold

class Tracker:
    __slots__ = (
        'tracks', '_iou_threshold', '_track_ttl', '_next_id', '_step',
        '_reid_threshold', '_confirmation_threshold', '_embeddings_count',
        '_track_gallery', '_gallery_ttl'
    )

    def __init__(
        self,
        iou_threshold: float,
        track_ttl: int = 5,
        step: int = 1,
        reid_threshold: float = 0.45,
        confirmation_threshold: int = 5,
        embeddings_count: int = 7,
        gallery_ttl: int = 1500,
    ):
        """
        Трекер лиц в видеопотоке.
        ---

        Базируется на IoU метрике и на реидентификации лиц.

        Args:
            iou_threshold (float): Порог метрики IoU для признания лица тем же треком.
            track_ttl (int, optional): Время жизни трека. Defaults to 5.
            step (int, optional): Частота вызова обновления треков. Defaults to 1.
            reid_threshold (float, optional): Минимальный порог схожести лиц при реидентификации. Defaults to 0.45.
            confirmation_threshold (int, optional): Минимальное количество обновлений для подтверждения трека. Defaults to 5.
            embeddings_count (int, optional): Максимальное количество хранимых эмбеддингов на трек. Defaults to 7.
            gallery_ttl (int, optional): Время жизни трека в галерее (в кадрах). Defaults to 1500 (~60 сек при 25fps).
        """
        self.tracks: List[Track] = []
        self._next_id = 0
        self._track_ttl = track_ttl
        self._iou_threshold = iou_threshold
        self._step = step
        self._reid_threshold = reid_threshold
        self._confirmation_threshold = confirmation_threshold
        self._embeddings_count = embeddings_count
        self._track_gallery: List[Track] = []
        self._gallery_ttl = gallery_ttl

    def _add_embedding(self, track: Track, emb: np.ndarray):
        """Добавляет эмбеддинг в трек с ограничением размера."""
        track.embeddings.append(emb)
        if len(track.embeddings) > self._embeddings_count:
            track.embeddings.pop(0)

    def _restore_from_gallery(self, bbox: CoordsXYWH, emb: np.ndarray, emotion: Dict, timestamp: float, d_idx: int) -> Track | None:
        """
        Поиск и восстановление трека из галереи по эмбеддингу.

        Returns:
            Track | None: Восстановленный трек или None если не найден.
        """
        best_track = None
        best_similarity = -1

        for archived_track in self._track_gallery:
            if not archived_track.embeddings:
                continue
            similarity = max(cosine_similarity(e, emb) for e in archived_track.embeddings)
            if similarity > best_similarity:
                best_similarity = similarity
                best_track = archived_track

        if best_track is not None and best_similarity >= self._reid_threshold:
            best_track.bbox = bbox
            best_track.age = 0
            best_track.gallery_age = 0
            best_track.emotion = emotion
            self._add_embedding(best_track, emb)
            best_track.history.append({'timestamp': timestamp, 'emotion': best_track.emotion})
            best_track.hits += 1
            best_track.confirmed = True  # трек уже был подтверждён ранее

            self._track_gallery.remove(best_track)
            self.tracks.append(best_track)
            return best_track

        return None

    def update(self, detections: List[CoordsXYWH], emotions: Dict[str, dict], faces: List[np.ndarray], embeddings: np.ndarray, timestamp: float = 0.0):
        """
        Обновление реальных состояний треков.
        ---

        Args:
            detections (List[CoordsXYWH]): Список детекций от детектора.
            emotions (Dict[str, dict]): Словарь с данными эмоций для каждого лица.
            faces (List[np.ndarray]): Кропы лиц.
            embeddings (np.ndarray): Эмбеддинги лиц.
            timestamp (float): Временная метка кадра в секундах.
        """
        # Обновляем галерею
        for t in self._track_gallery:
            t.gallery_age += 1
        self._track_gallery = [t for t in self._track_gallery if t.gallery_age < self._gallery_ttl]

        if not detections:
            for track in self.tracks:
                track.age += 1
            expired = [t for t in self.tracks if t.age >= self._track_ttl]
            self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
            for t in expired:
                if t.confirmed and t.embeddings:
                    self._track_gallery.append(t)
            return

        if not self.tracks:
            for i, bbox in enumerate(detections):
                emotion = emotions.get(f'face_{i}', {})
                emb = embeddings[i] if len(embeddings) > i else np.zeros(512, dtype=np.float32)

                # Сначала ищем в галерее
                restored = self._restore_from_gallery(bbox, emb, emotion, timestamp, i)
                if restored is None:
                    track = Track(
                        track_id=self._next_id, bbox=bbox, emotion=emotion,
                        embedding=emb, image=faces[i],
                        identity_threshold=self._reid_threshold
                    )
                    track.history.append({'timestamp': timestamp, 'emotion': emotion})
                    self.tracks.append(track)
                    self._next_id += 1
            return

        iou_matrix = np.zeros((len(self.tracks), len(detections)), dtype=float)
        for t_idx, d_idx in product(range(len(self.tracks)), range(len(detections))):
            iou_matrix[t_idx, d_idx] = IoU(self.tracks[t_idx].bbox, detections[d_idx])

        matched_tracks = set()
        matched_detections = set()

        # IoU-матчинг
        while True:
            if np.max(iou_matrix) < self._iou_threshold:
                break

            t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)

            track = self.tracks[t_idx]
            new_emb = embeddings[d_idx] if len(embeddings) > d_idx else None

            # IoU гарантирует пространственное совпадение — матчим всегда.
            # Эмбеддинг обновляем только если лицо похоже, чтобы не засорять галерею чужими данными.
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
                if not track.embeddings or track.check_identity(new_emb):
                    self._add_embedding(track, new_emb)

            track.history.append({'timestamp': timestamp, 'emotion': track.emotion})
            track.hits += 1

            if track.hits >= self._confirmation_threshold:
                track.confirmed = True

            matched_tracks.add(t_idx)
            matched_detections.add(d_idx)

            iou_matrix[t_idx, :] = -1
            iou_matrix[:, d_idx] = -1

        # ReID среди активных unmatched треков, затем поиск в галерее
        for d_idx, bbox in enumerate(detections):
            if d_idx in matched_detections:
                continue

            emb = embeddings[d_idx] if len(embeddings) > d_idx else None
            emotion = emotions.get(f'face_{d_idx}', {})

            best_track = None
            best_similarity = -1

            # 1. Ищем среди активных треков
            if emb is not None:
                for t_idx, track in enumerate(self.tracks):
                    if t_idx in matched_tracks:
                        continue
                    if not track.embeddings:
                        continue
                    similarity = max(cosine_similarity(e, emb) for e in track.embeddings)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_track = track

            if best_track is not None and best_similarity >= self._reid_threshold:
                best_track.bbox = bbox
                best_track.age = 0
                best_track.emotion = emotion
                if emb is not None:
                    self._add_embedding(best_track, emb)
                best_track.history.append({'timestamp': timestamp, 'emotion': best_track.emotion})
                best_track.hits += 1
                if best_track.hits >= self._confirmation_threshold:
                    best_track.confirmed = True
                matched_detections.add(d_idx)
                matched_tracks.add(self.tracks.index(best_track))

            else:
                # 2. Ищем в галерее (лицо пропадало из кадра)
                if emb is not None:
                    restored = self._restore_from_gallery(bbox, emb, emotion, timestamp, d_idx)
                    if restored is not None:
                        matched_detections.add(d_idx)
                        matched_tracks.add(len(self.tracks) - 1)
                        continue

                # 3. Создаём новый трек
                emb_for_track = emb if emb is not None else np.zeros(512, dtype=np.float32)
                track = Track(
                    track_id=self._next_id, bbox=bbox, emotion=emotion,
                    embedding=emb_for_track, image=faces[d_idx],
                    identity_threshold=self._reid_threshold
                )
                track.history.append({'timestamp': timestamp, 'emotion': emotion})
                self.tracks.append(track)
                self._next_id += 1

        # Увеличиваем age неподтверждённым трекам
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.age += 1

        # Перемещаем истёкшие confirmed треки в галерею
        expired = [t for t in self.tracks if t.age >= self._track_ttl]
        self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
        for t in expired:
            if t.confirmed and t.embeddings:
                self._track_gallery.append(t)

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