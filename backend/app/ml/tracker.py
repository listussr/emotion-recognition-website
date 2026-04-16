import numpy as np
from typing import Dict, List, Optional, Sequence, Tuple

from scipy.optimize import linear_sum_assignment

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

def topk_mean_similarity(embeddings_list: np.ndarray, query: np.ndarray, k: int = 3):
    """
    Усреднение `k` наиболее сходных эмбеддингов.
    ---

    Чтобы эмбеддинг смазанного лица не портил оригинальные эмбеддинги.

    Args:
        embeddings_list (np.ndarray): Имеющиеся эмбеддинги лица.
        query (np.ndarray): Новый эмбеддинг.
        k (int, optional): int. Defaults to 3.

    Returns:
        float: Среднее значение топ `k` эмбеддингов.
    """
    if not embeddings_list:
        return -1.0
    sims = np.array([cosine_similarity(e, query) for e in embeddings_list])
    k = min(k, len(sims))
    return float(np.mean(np.sort(sims)[-k:]))

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

_EMA_ALPHA = 0.9  # вес старого прототипа в EMA-обновлении


def proto_similarity(track: 'Track', query: np.ndarray) -> float:
    """
    C1. Косинусное сходство запроса с EMA-прототипом трека.
    ---

    EMA-прототип (`track.proto`) — это экспоненциально сглаженное среднее всех
    добавленных в трек эмбеддингов (нормализованное)

    Returns:
        float: косинусное сходство в [-1, 1] или -1.0, если у трека нет прототипа.
    """
    if track.proto is None:
        return -1.0
    return cosine_similarity(track.proto, query)


class Track:
    __slots__ = (
        'id', 'bbox', 'image', 'velocity', 'age', 'emotion',
        'history', 'embeddings', 'identity_threshold', 'hits',
        'confirmed', 'gallery_age', 'bootstrap_count', 'proto'
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
        self.bootstrap_count = 1 if embedding is not None else 0
        if embedding is not None:
            p = np.asarray(embedding, dtype=np.float32).flatten()
            n = float(np.linalg.norm(p))
            self.proto = (p / n) if n > 0 else None
        else:
            self.proto = None

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

        if self.proto is not None:
            return cosine_similarity(self.proto, embedding) >= self.identity_threshold

        return topk_mean_similarity(self.embeddings, embedding) >= self.identity_threshold

    def should_store(self, embedding: np.ndarray, thresh: float, bootstrap: int = 3) -> bool:
        """
        Решение о добавлении эмбеддинга в буфер трека. (A6)
        ---

        Логика:
         * Первые `bootstrap` эмбеддингов добавляются без проверки — нужна вариативность поз.
         * Далее эмбеддинг добавляется только если его *средняя* косинусная схожесть
           со всеми уже сохранёнными ≥ `thresh`. Используется mean, а не max —
           чтобы один-единственный близкий эмбеддинг не мог протащить «своих».

        Args:
            embedding (np.ndarray): Новый эмбеддинг.
            thresh (float): Порог средней косинусной схожести.
            bootstrap (int): Количество «загрузочных» эмбеддингов без проверки.

        Returns:
            bool: Нужно ли сохранять эмбеддинг в треке.
        """
        if not self.embeddings:
            return True
        if self.bootstrap_count < bootstrap:
            return True
        # C1: сравниваем с EMA-прототипом — он уже представляет "среднее"
        # лицо трека лучше, чем mean по буферу (устойчив к дубликатам и старым кадрам).
        if self.proto is not None:
            return float(cosine_similarity(self.proto, embedding)) >= thresh
        sims = [cosine_similarity(e, embedding) for e in self.embeddings]
        return float(np.mean(sims)) >= thresh

class Tracker:
    __slots__ = (
        'tracks', '_iou_threshold', '_track_ttl', '_next_id', '_step',
        '_reid_threshold', '_reid_threshold_gallery', '_embedding_store_threshold',
        '_confirmation_threshold', '_embeddings_count',
        '_track_gallery', '_gallery_ttl', '_unconfirmed_gallery_ttl'
    )

    def __init__(
        self,
        iou_threshold: float,
        track_ttl: int = 5,
        step: int = 1,
        reid_threshold: float = 0.45,
        reid_threshold_gallery: float = 0.50,
        embedding_store_threshold: float = 0.50,
        confirmation_threshold: int = 5,
        embeddings_count: int = 7,
        gallery_ttl: int = 1500,
        unconfirmed_gallery_ttl: int = 750,
    ):
        """
        Трекер лиц в видеопотоке.
        ---

        Базируется на IoU метрике и на реидентификации лиц.

        Args:
            iou_threshold (float): Порог метрики IoU для признания лица тем же треком.
            track_ttl (int, optional): Время жизни трека. Defaults to 5.
            step (int, optional): Частота вызова обновления треков. Defaults to 1.
            reid_threshold (float, optional): Порог схожести для активного ReID (среди живых треков). Defaults to 0.45.
            reid_threshold_gallery (float, optional): Порог схожести для восстановления из галереи (строже). Defaults to 0.50.
            embedding_store_threshold (float, optional): Порог средней схожести для добавления эмбеддинга в буфер трека (A6). Defaults to 0.50.
            confirmation_threshold (int, optional): Минимальное количество обновлений для подтверждения трека. Defaults to 5.
            embeddings_count (int, optional): Максимальное количество хранимых эмбеддингов на трек. Defaults to 7.
            gallery_ttl (int, optional): Время жизни подтверждённого трека в галерее. Defaults to 1500 (~60 сек при 25fps).
            unconfirmed_gallery_ttl (int, optional): Время жизни неподтверждённого трека в галерее. Defaults to 750.
        """
        self.tracks: List[Track] = []
        self._next_id = 0
        self._track_ttl = track_ttl
        self._iou_threshold = iou_threshold
        self._step = step
        self._reid_threshold = reid_threshold
        self._reid_threshold_gallery = reid_threshold_gallery
        self._embedding_store_threshold = embedding_store_threshold
        self._confirmation_threshold = confirmation_threshold
        self._embeddings_count = embeddings_count
        self._track_gallery: List[Track] = []
        self._gallery_ttl = gallery_ttl
        self._unconfirmed_gallery_ttl = unconfirmed_gallery_ttl

    def _add_embedding(self, track: Track, emb: np.ndarray):
        """
        Добавляет эмбеддинг в трек с ограничением размера и строгим гейтом.
        ---

        Гейт `should_store` отбрасывает эмбеддинги, которые существенно отличаются
        от уже сохранённых — предотвращает засорение трека шумными/повернутыми
        лицами. Первые несколько эмбеддингов добавляются без проверки.
        """
        if emb is None:
            return
        if not track.should_store(emb, self._embedding_store_threshold):
            return
        track.embeddings.append(emb)
        track.bootstrap_count += 1
        if len(track.embeddings) > self._embeddings_count:
            track.embeddings.pop(0)

        # обновление EMA-прототипа, затем L2-нормализация
        emb_arr = np.asarray(emb, dtype=np.float32).flatten()
        if track.proto is None:
            n = float(np.linalg.norm(emb_arr))
            track.proto = (emb_arr / n) if n > 0 else None
        else:
            new_proto = _EMA_ALPHA * track.proto + (1.0 - _EMA_ALPHA) * emb_arr
            n = float(np.linalg.norm(new_proto))
            if n > 0:
                track.proto = new_proto / n

    def _restore_from_gallery(self, bbox: CoordsXYWH, emb: Optional[np.ndarray], emotion: Dict, timestamp: float, d_idx: int) -> Optional[Track]:
        """
        Поиск и восстановление трека из галереи по эмбеддингу.
        ---

        Returns:
            Optional[Track]: Восстановленный трек или None если не найден.
        """
        if emb is None:
            return None

        best_track = None
        best_similarity = -1.0

        for archived_track in self._track_gallery:
            if archived_track.proto is None:
                continue
            similarity = proto_similarity(archived_track, emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_track = archived_track

        if best_track is not None and best_similarity >= self._reid_threshold_gallery:
            best_track.bbox = bbox
            best_track.age = 0
            best_track.gallery_age = 0
            best_track.emotion = emotion
            self._add_embedding(best_track, emb)
            best_track.history.append({'timestamp': timestamp, 'emotion': best_track.emotion})
            if not best_track.confirmed:
                best_track.hits += 1
            best_track.confirmed = True

            self._track_gallery.remove(best_track)
            self.tracks.append(best_track)
            return best_track

        return None

    def _get_emb(self, embeddings: Sequence[Optional[np.ndarray]], idx: int) -> Optional[np.ndarray]:
        """Безопасное извлечение эмбеддинга с поддержкой None."""
        if idx >= len(embeddings):
            return None
        e = embeddings[idx]
        if e is None:
            return None
        e = np.asarray(e)
        if e.size == 0:
            return None
        return e

    def _apply_match(self, track: Track, d_idx: int, detections: List[CoordsXYWH],
                     emotions: Dict[str, dict], embeddings: Sequence[Optional[np.ndarray]],
                     timestamp: float, update_velocity: bool = True):
        """
        Применить назначение детекции `d_idx` треку `track`:
        обновить bbox/velocity/age, зафиксировать эмоцию, добавить эмбеддинг (через гейт),
        увеличить hits и при достижении порога подтвердить.
        """
        new_bbox = detections[d_idx]
        new_emb = self._get_emb(embeddings, d_idx)

        if update_velocity:
            if track.age > 0:
                track.velocity = (0.0, 0.0, 0.0, 0.0)
            else:
                track.velocity = (
                    (new_bbox[0] - track.bbox[0]) / self._step,
                    (new_bbox[1] - track.bbox[1]) / self._step,
                    (new_bbox[2] - track.bbox[2]) / self._step,
                    (new_bbox[3] - track.bbox[3]) / self._step,
                )

                max_dx = 0.5 * new_bbox[2] / max(self._step, 1)
                max_dy = 0.5 * new_bbox[3] / max(self._step, 1)
                track.velocity = (
                    float(np.clip(track.velocity[0], -max_dx, max_dx)),
                    float(np.clip(track.velocity[1], -max_dy, max_dy)),
                    float(np.clip(track.velocity[2], -max_dx, max_dx)),
                    float(np.clip(track.velocity[3], -max_dy, max_dy)),
                )
        track.bbox = new_bbox
        track.age = 0
        track.emotion = emotions.get(f'face_{d_idx}', track.emotion)

        self._add_embedding(track, new_emb)

        track.history.append({'timestamp': timestamp, 'emotion': track.emotion})
        track.hits += 1
        if track.hits >= self._confirmation_threshold:
            track.confirmed = True

    def update(self, detections: List[CoordsXYWH], emotions: Dict[str, dict], faces: List[np.ndarray],
               embeddings: Sequence[Optional[np.ndarray]], timestamp: float = 0.0):
        """
        Обновление реальных состояний треков.
        ---

        Args:
            detections (List[CoordsXYWH]): Список детекций от детектора.
            emotions (Dict[str, dict]): Словарь с данными эмоций для каждого лица.
            faces (List[np.ndarray]): Кропы лиц.
            embeddings (Sequence[Optional[np.ndarray]]): Эмбеддинги лиц.
                Допускается None на позициях, где отбраковано лицо по качеству позы -
                такое лицо трекается по IoU, но не влияет на ReID-матчинг и не идёт в буфер.
            timestamp (float): Временная метка кадра в секундах.
        """
        for t in self._track_gallery:
            t.gallery_age += 1
        self._track_gallery = [
            t for t in self._track_gallery
            if t.gallery_age < (self._gallery_ttl if t.confirmed else self._unconfirmed_gallery_ttl)
        ]

        if not detections:
            for track in self.tracks:
                track.age += 1
            expired = [t for t in self.tracks if t.age >= self._track_ttl]
            self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
            # архивируем и неподтверждённые треки
            for t in expired:
                if t.embeddings:
                    self._track_gallery.append(t)
            return

        if not self.tracks:
            for i, bbox in enumerate(detections):
                emotion = emotions.get(f'face_{i}', {})
                emb = self._get_emb(embeddings, i)

                # Сначала ищем в галерее. Если эмбеддинга нет (B2 отбраковал), пропускаем галерею.
                restored = self._restore_from_gallery(bbox, emb, emotion, timestamp, i) if emb is not None else None
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

        n_t, n_d = len(self.tracks), len(detections)
        matched_tracks: set = set()
        matched_detections: set = set()


        INF = 1.0
        cost = np.full((n_t, n_d), INF, dtype=np.float32)
        for t_idx in range(n_t):
            track = self.tracks[t_idx]
            for d_idx in range(n_d):
                iou = IoU(track.bbox, detections[d_idx])
                if iou < self._iou_threshold:
                    continue
                d_emb = self._get_emb(embeddings, d_idx)
                sim = 0.0
                if track.proto is not None and d_emb is not None:
                    sim = max(proto_similarity(track, d_emb), 0.0)
                cost[t_idx, d_idx] = 1.0 - (0.7 * iou + 0.3 * sim)

        row_ind, col_ind = linear_sum_assignment(cost)
        for t_idx, d_idx in zip(row_ind, col_ind):
            if cost[t_idx, d_idx] >= INF:
                continue  # пара не прошла IoU-порог
            self._apply_match(self.tracks[t_idx], int(d_idx), detections, emotions, embeddings, timestamp)
            matched_tracks.add(int(t_idx))
            matched_detections.add(int(d_idx))

        # reid среди активных unmatched треков, затем поиск в галерее
        for d_idx, bbox in enumerate(detections):
            if d_idx in matched_detections:
                continue

            emb = self._get_emb(embeddings, d_idx)
            emotion = emotions.get(f'face_{d_idx}', {})

            best_track = None
            best_t_idx = -1
            best_similarity = -1.0

            # 1. Ищем среди активных unmatched треков.
            if emb is not None:
                for t_idx, track in enumerate(self.tracks):
                    if t_idx in matched_tracks:
                        continue
                    if track.proto is None:
                        continue
                    similarity = proto_similarity(track, emb)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_track = track
                        best_t_idx = t_idx

            if best_track is not None and best_similarity >= self._reid_threshold:
                self._apply_match(best_track, d_idx, detections, emotions, embeddings,
                                  timestamp, update_velocity=False)
                matched_detections.add(d_idx)
                matched_tracks.add(best_t_idx)
                continue

            # 2. Ищем в галерее (лицо пропадало из кадра). Только если есть эмбеддинг.
            if emb is not None:
                restored = self._restore_from_gallery(bbox, emb, emotion, timestamp, d_idx)
                if restored is not None:
                    matched_detections.add(d_idx)
                    # Новый индекс в self.tracks - последний (restored только что добавлен).
                    matched_tracks.add(len(self.tracks) - 1)
                    continue

            # 3. Создаём новый трек.
            track = Track(
                track_id=self._next_id, bbox=bbox, emotion=emotion,
                embedding=emb, image=faces[d_idx],
                identity_threshold=self._reid_threshold
            )
            track.history.append({'timestamp': timestamp, 'emotion': emotion})
            self.tracks.append(track)
            self._next_id += 1

        # Увеличиваем age неподтверждённым трекам
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.age += 1

        # архивируем истёкшие треки - и подтверждённые
        expired = [t for t in self.tracks if t.age >= self._track_ttl]
        self.tracks = [t for t in self.tracks if t.age < self._track_ttl]
        for t in expired:
            if t.embeddings:
                self._track_gallery.append(t)

    def predict(self):
        """
        Обновление треков путём предсказания движения.
        ---
        """
        for track in self.tracks:
            track.bbox = track.move()
        self.tracks = [t for t in self.tracks if t.age < self._track_ttl]


    def get_tracks(self) -> List[Track]:
        """
        Получение состояний треков.
        ---

        Returns:
            List[Track]: Состояния текущих треков.
        """
        return [t for t in self.tracks if t.confirmed]