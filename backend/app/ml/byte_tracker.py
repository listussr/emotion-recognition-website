from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment

def _xywh_to_xyah(bbox: np.ndarray) -> np.ndarray:
    """(x, y, w, h) → (cx, cy, aspect_ratio=w/h, h). Формат состояния Kalman."""
    cx = bbox[0] + bbox[2] / 2
    cy = bbox[1] + bbox[3] / 2
    a = bbox[2] / max(bbox[3], 1e-6)
    h = bbox[3]
    return np.array([cx, cy, a, h], dtype=np.float32)


def _xyah_to_xywh(state: np.ndarray) -> np.ndarray:
    """(cx, cy, a, h) → (x, y, w, h)."""
    h = state[3]
    w = state[2] * h
    x = state[0] - w / 2
    y = state[1] - h / 2
    return np.array([x, y, w, h], dtype=np.float32)


def _iou_matrix(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """IoU между каждой парой bbox в формате (x, y, w, h). Shape (Na, Nb)."""
    if len(boxes_a) == 0 or len(boxes_b) == 0:
        return np.zeros((len(boxes_a), len(boxes_b)), dtype=np.float32)
    a = np.asarray(boxes_a, dtype=np.float32)
    b = np.asarray(boxes_b, dtype=np.float32)
    a_x2 = a[:, 0] + a[:, 2]
    a_y2 = a[:, 1] + a[:, 3]
    b_x2 = b[:, 0] + b[:, 2]
    b_y2 = b[:, 1] + b[:, 3]

    inter_x1 = np.maximum(a[:, None, 0], b[None, :, 0])
    inter_y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    inter_x2 = np.minimum(a_x2[:, None], b_x2[None, :])
    inter_y2 = np.minimum(a_y2[:, None], b_y2[None, :])

    inter_w = np.clip(inter_x2 - inter_x1, 0, None)
    inter_h = np.clip(inter_y2 - inter_y1, 0, None)
    inter = inter_w * inter_h

    area_a = (a[:, 2] * a[:, 3])[:, None]
    area_b = (b[:, 2] * b[:, 3])[None, :]
    union = area_a + area_b - inter + 1e-6
    return inter / union



class _KalmanFilter:
    """
    Простой Kalman-фильтр с моделью постоянной скорости.
    """

    _STD_W_POS = 1.0 / 20
    _STD_W_VEL = 1.0 / 160

    def __init__(self) -> None:
        ndim, dt = 4, 1.0
        self._F = np.eye(2 * ndim, dtype=np.float32)
        for i in range(ndim):
            self._F[i, ndim + i] = dt
        self._H = np.eye(ndim, 2 * ndim, dtype=np.float32)

    def initiate(self, measurement: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        mean_pos = measurement.astype(np.float32)
        mean_vel = np.zeros_like(mean_pos)
        mean = np.concatenate([mean_pos, mean_vel])
        h = measurement[3]
        std = np.array([
            2 * self._STD_W_POS * h, 2 * self._STD_W_POS * h, 1e-2, 2 * self._STD_W_POS * h,
            10 * self._STD_W_VEL * h, 10 * self._STD_W_VEL * h, 1e-5, 10 * self._STD_W_VEL * h,
        ], dtype=np.float32)
        cov = np.diag(std * std)
        return mean, cov

    def predict(self, mean: np.ndarray, cov: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        h = mean[3]
        std_pos = np.array([self._STD_W_POS * h, self._STD_W_POS * h, 1e-2, self._STD_W_POS * h])
        std_vel = np.array([self._STD_W_VEL * h, self._STD_W_VEL * h, 1e-5, self._STD_W_VEL * h])
        Q = np.diag(np.concatenate([std_pos, std_vel]) ** 2).astype(np.float32)
        mean = self._F @ mean
        cov = self._F @ cov @ self._F.T + Q
        return mean, cov

    def update(self, mean: np.ndarray, cov: np.ndarray,
               measurement: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        h = mean[3]
        std = np.array([self._STD_W_POS * h, self._STD_W_POS * h, 1e-1, self._STD_W_POS * h])
        R = np.diag(std * std).astype(np.float32)
        proj_mean = self._H @ mean
        proj_cov = self._H @ cov @ self._H.T + R

        K = np.linalg.solve(proj_cov.T, (cov @ self._H.T).T).T
        innovation = measurement - proj_mean
        new_mean = mean + K @ innovation
        new_cov = cov - K @ proj_cov @ K.T
        return new_mean, new_cov


class _TrackState:
    NEW = 0
    TRACKED = 1
    LOST = 2
    REMOVED = 3

class STrack:
    """
    Один трек. Хранит Kalman-состояние + бизнес-данные (эмоции, история),
    которые потребляются video_pipeline'ом, + галерею ArcFace-эмбеддингов
    для ReID.
    """
    _kalman = _KalmanFilter()  # один фильтр на всех — статлеса нет

    def __init__(self, bbox_xywh: np.ndarray, score: float, track_id: int,
                 gallery_size: int = 15) -> None:
        self.id: int = track_id
        self.score: float = float(score)

        self._mean, self._cov = self._kalman.initiate(_xywh_to_xyah(bbox_xywh))
        self.state: int = _TrackState.NEW
        self.frames_since_update: int = 0
        self.hits: int = 1

        self.emotion: Optional[Dict] = None
        self.history: List[Dict] = []
        self.image: Optional[np.ndarray] = None
        self._gallery: Deque[np.ndarray] = deque(maxlen=gallery_size)
        self._centroid: Optional[np.ndarray] = None

    def add_embedding(self, emb: np.ndarray) -> None:
        """Добавить эмбеддинг в галерею и обновить centroid."""
        if emb is None:
            return
        self._gallery.append(emb)
        avg = np.mean(np.stack(list(self._gallery), axis=0), axis=0)
        norm = float(np.linalg.norm(avg))
        self._centroid = avg / norm if norm > 1e-6 else None

    def cosine_to(self, emb: np.ndarray) -> float:
        """Cosine similarity центроида трека с заданным эмбеддингом."""
        if self._centroid is None or emb is None:
            return -1.0
        return float(np.dot(self._centroid, emb))

    @property
    def has_embedding(self) -> bool:
        return self._centroid is not None

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """Текущий предсказанный bbox в формате (x, y, w, h), int."""
        b = _xyah_to_xywh(self._mean[:4])
        return int(b[0]), int(b[1]), int(b[2]), int(b[3])

    def predict(self) -> None:
        """Kalman-предикт: подвинуть позицию по последней скорости."""
        self._mean, self._cov = self._kalman.predict(self._mean, self._cov)
        self.frames_since_update += 1

    def update(self, bbox_xywh: np.ndarray, score: float) -> None:
        """Kalman-апдейт после успешной ассоциации с детекцией."""
        meas = _xywh_to_xyah(bbox_xywh)
        self._mean, self._cov = self._kalman.update(self._mean, self._cov, meas)
        self.score = float(score)
        self.frames_since_update = 0
        self.hits += 1

def _hungarian_match(cost: np.ndarray, threshold: float) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Линейный assignment по матрице стоимости.

    Args:
        cost: shape (N_tracks, N_dets), cost = 1 - IoU.
        threshold: пара ассоциируется только если IoU >= threshold,
                   т.е. cost <= 1 - threshold.

    Returns:
        matches: список пар (track_idx, det_idx).
        unmatched_tracks: индексы треков без пары.
        unmatched_dets: индексы детекций без пары.
    """
    if cost.size == 0:
        return [], list(range(cost.shape[0])), list(range(cost.shape[1]))
    rows, cols = linear_sum_assignment(cost)
    matches: List[Tuple[int, int]] = []
    matched_rows, matched_cols = set(), set()
    cost_thresh = 1.0 - threshold
    for r, c in zip(rows, cols):
        if cost[r, c] <= cost_thresh:
            matches.append((int(r), int(c)))
            matched_rows.add(int(r))
            matched_cols.add(int(c))
    unmatched_tracks = [i for i in range(cost.shape[0]) if i not in matched_rows]
    unmatched_dets = [i for i in range(cost.shape[1]) if i not in matched_cols]
    return matches, unmatched_tracks, unmatched_dets


class BYTETracker:
    """
    Сам ByteTrack. Все треки живут здесь, в трёх корзинах:
    `_active` — TRACKED, `_lost` — LOST, `_removed` — REMOVED.
    """

    def __init__(
        self,
        track_thresh: float = 0.5,
        match_thresh: float = 0.7,
        track_buffer: int = 30,
        new_track_thresh: float = 0.6,
        min_hits_to_confirm: int = 2,
        reid_threshold: float = 0.4,
        gallery_size: int = 15,
    ) -> None:
        """
        Args:
            track_thresh: порог разделения на high/low conf детекции.
                Детекции со score >= track_thresh идут на 1-й этап матчинга,
                ниже — на 2-й.
            match_thresh: минимальный IoU, при котором пара ассоциируется
                на 1-м этапе. На 2-м используется более мягкий порог 0.5.
            track_buffer: на сколько кадров без апдейта трек переходит в
                LOST до полного REMOVED.
            new_track_thresh: новый трек создаётся только из детекции с
                score >= new_track_thresh — отсекает совсем шумные ложные
                детекции.
            min_hits_to_confirm: трек считается «подтверждённым» (выдаётся
                в get_tracks()) после такого числа успешных апдейтов.
                Защита от вспышек однокадровых ложных срабатываний.
        """
        self.track_thresh = track_thresh
        self.match_thresh = match_thresh
        self.track_buffer = track_buffer
        self.new_track_thresh = new_track_thresh
        self.min_hits_to_confirm = min_hits_to_confirm
        self.reid_threshold = reid_threshold
        self.gallery_size = gallery_size

        self._active: List[STrack] = []
        self._lost: List[STrack] = []
        self._next_id = 1

    def _new_id(self) -> int:
        i = self._next_id
        self._next_id += 1
        return i

    def update(self, bboxes_with_scores: List[Tuple[float, float, float, float, float]],
               embeddings: Optional[List[np.ndarray]] = None,
               quality_mask: Optional[List[bool]] = None,
               ) -> Tuple[List[STrack], List[int]]:
        """
        Один шаг ассоциации на detection-кадре.

        Args:
            bboxes_with_scores: список (x, y, w, h, score). score из детектора
                (BlazeFace conf), используется для двухстадийного матчинга.
            embeddings: ArcFace L2-нормированные эмбеддинги по каждой детекции.
                Используются для стадии 3 — ReID-связки потерянных треков с
                новыми детекциями. Если None — стадия 3 пропускается.
            quality_mask: список bool того же размера. Эмбеддинг кладётся в
                галерею трека только если quality_mask[i] == True (хорошая
                поза, достаточный размер лица) — иначе галерея загрязняется.
                Сравнение cosine similarity делается всегда.

        Returns:
            tracks: текущий список **подтверждённых** треков (NEW не выдаём).
            det_to_track_id: список длиной len(bboxes_with_scores), для каждой
                детекции — id трека, к которому её приклеили (или -1, если
                она была отвергнута как новая, но ниже new_track_thresh).
                video_pipeline использует это, чтобы привязать softmax-эмоции
                к нужному треку.
        """
        det_to_track_id = [-1] * len(bboxes_with_scores)

        def _emb_for(det_idx: int) -> Optional[np.ndarray]:
            """Эмбеддинг детекции, если он есть."""
            if embeddings is None or det_idx >= len(embeddings):
                return None
            return embeddings[det_idx]

        def _store_emb(track: STrack, det_idx: int) -> None:
            """
            Положить эмбеддинг в галерею трека.
            ---

            Раньше мы фильтровали по quality_mask (frontality / size), но
            на видео с разговорными ракурсами это часто полностью блокировало
            заполнение галереи — и стадия 3 ReID не имела что сравнивать.
            Теперь храним все эмбеддинги; centroid усредняет шум, а порог
            cosine защищает от ложных срабатываний.
            """
            if embeddings is None or det_idx >= len(embeddings):
                return
            track.add_embedding(embeddings[det_idx])

        for t in self._active:
            t.predict()
        for t in self._lost:
            t.predict()

        high_idx, low_idx = [], []
        for i, det in enumerate(bboxes_with_scores):
            score = det[4]
            if score >= self.track_thresh:
                high_idx.append(i)
            elif score > 0.1:
                low_idx.append(i)

        det_bboxes = np.array(
            [[d[0], d[1], d[2], d[3]] for d in bboxes_with_scores],
            dtype=np.float32,
        ) if bboxes_with_scores else np.zeros((0, 4), dtype=np.float32)

        pool = self._active + self._lost
        pool_bboxes = np.array([t.bbox for t in pool], dtype=np.float32) \
            if pool else np.zeros((0, 4), dtype=np.float32)

        if pool and high_idx:
            iou1 = _iou_matrix(pool_bboxes, det_bboxes[high_idx])
            cost1 = 1.0 - iou1
            matches1, u_tracks1, u_dets1 = _hungarian_match(cost1, self.match_thresh)
        else:
            matches1, u_tracks1, u_dets1 = [], list(range(len(pool))), list(range(len(high_idx)))

        for ti, di in matches1:
            track = pool[ti]
            det_pos = high_idx[di]
            det = bboxes_with_scores[det_pos]
            track.update(np.array([det[0], det[1], det[2], det[3]]), det[4])
            track.state = _TrackState.TRACKED
            _store_emb(track, det_pos)
            det_to_track_id[det_pos] = track.id

        active_unmatched = [pool[i] for i in u_tracks1 if pool[i].state == _TrackState.TRACKED]
        active_unmatched_global_idx = [i for i in u_tracks1 if pool[i].state == _TrackState.TRACKED]
        active_bboxes = np.array([t.bbox for t in active_unmatched], dtype=np.float32) \
            if active_unmatched else np.zeros((0, 4), dtype=np.float32)

        if active_unmatched and low_idx:
            iou2 = _iou_matrix(active_bboxes, det_bboxes[low_idx])
            cost2 = 1.0 - iou2
            matches2, _, _ = _hungarian_match(cost2, 0.5)
        else:
            matches2 = []

        matched_active_local = set()
        for ti, di in matches2:
            track = active_unmatched[ti]
            det_pos = low_idx[di]
            det = bboxes_with_scores[det_pos]
            track.update(np.array([det[0], det[1], det[2], det[3]]), det[4])
            track.state = _TrackState.TRACKED
            _store_emb(track, det_pos)
            det_to_track_id[det_pos] = track.id
            matched_active_local.add(ti)


        for li in u_tracks1:
            t = pool[li]
            if t in active_unmatched and active_unmatched.index(t) in matched_active_local:
                continue
            t.state = _TrackState.LOST

        reid_matched_dets: set = set()
        if embeddings is not None and self._lost and u_dets1:
            lost_with_emb: List[STrack] = [
                t for t in self._lost
                if t.has_embedding and t.state == _TrackState.LOST
            ]
            reid_dets: List[Tuple[int, int, np.ndarray]] = []
            for u_idx_local, u_idx in enumerate(u_dets1):
                det_pos = high_idx[u_idx]
                emb = _emb_for(det_pos)
                if emb is None:
                    continue
                reid_dets.append((u_idx_local, det_pos, emb))

            if lost_with_emb and reid_dets:
                cost3 = np.ones((len(lost_with_emb), len(reid_dets)), dtype=np.float32)
                for ti, t in enumerate(lost_with_emb):
                    for di, (_, _, emb) in enumerate(reid_dets):
                        cost3[ti, di] = 1.0 - t.cosine_to(emb)
                matches3, _, _ = _hungarian_match(cost3, self.reid_threshold)
                for ti, di in matches3:
                    track = lost_with_emb[ti]
                    u_idx_local, det_pos, emb = reid_dets[di]
                    det = bboxes_with_scores[det_pos]
                    sim = track.cosine_to(emb)
                    fsu_before = track.frames_since_update
                    track.update(np.array([det[0], det[1], det[2], det[3]]), det[4])
                    track.state = _TrackState.TRACKED
                    track.add_embedding(emb)
                    det_to_track_id[det_pos] = track.id
                    reid_matched_dets.add(u_idx_local)
                    print(f"[ByteTrack ReID] track #{track.id} reactivated "
                          f"after {fsu_before} frames (cosine={sim:.3f})",
                          flush=True)

        for u_idx_local, di in enumerate(u_dets1):
            if u_idx_local in reid_matched_dets:
                continue
            det_pos = high_idx[di]
            det = bboxes_with_scores[det_pos]
            if det[4] < self.new_track_thresh:
                continue
            new_track = STrack(
                np.array([det[0], det[1], det[2], det[3]]),
                det[4],
                self._new_id(),
                gallery_size=self.gallery_size,
            )
            self._active.append(new_track)
            _store_emb(new_track, det_pos)
            det_to_track_id[det_pos] = new_track.id

        new_active: List[STrack] = []
        new_lost: List[STrack] = []
        for t in self._active + self._lost:
            if t in [na for na in new_active]:
                continue
            if t.state == _TrackState.TRACKED:
                new_active.append(t)
            elif t.state == _TrackState.LOST or t.state == _TrackState.NEW:
                if t.frames_since_update <= self.track_buffer:
                    new_lost.append(t)

        for t in self._active:
            if t not in new_active and t not in new_lost and t.state == _TrackState.TRACKED:
                new_active.append(t)
        self._active = new_active
        self._lost = new_lost

        return self.get_tracks(), det_to_track_id

    def predict(self) -> None:
        """Шаг предсказания на non-detection кадре. Только Kalman-предикт."""
        for t in self._active:
            t.predict()
        for t in self._lost:
            t.predict()

    def get_tracks(self) -> List[STrack]:
        """Подтверждённые активные треки. NEW и LOST не выдаём наружу."""
        return [t for t in self._active
                if t.state == _TrackState.TRACKED and t.hits >= self.min_hits_to_confirm]


class Tracker:
    """
    Адаптер ByteTrack под интерфейс старого трекера, чтобы video_pipeline
    остался почти неизменным. Ведёт EMA-сглаживание эмоций и историю
    предсказаний по timestamp'ам поверх ByteTrack-ассоциаций.
    """

    def __init__(
        self,
        track_thresh: float = 0.5,
        match_thresh: float = 0.7,
        track_buffer: int = 30,
        new_track_thresh: float = 0.6,
        min_hits_to_confirm: int = 2,
        emotion_ema_alpha: float = 0.75,
        reid_threshold: float = 0.4,
        gallery_size: int = 15,
    ) -> None:
        self._byte = BYTETracker(
            track_thresh=track_thresh,
            match_thresh=match_thresh,
            track_buffer=track_buffer,
            new_track_thresh=new_track_thresh,
            min_hits_to_confirm=min_hits_to_confirm,
            reid_threshold=reid_threshold,
            gallery_size=gallery_size,
        )
        self._alpha = emotion_ema_alpha

    def update(
        self,
        bboxes_with_scores: List[Tuple[float, float, float, float, float]],
        emotions_per_det: List[Optional[Dict]],
        timestamp: float,
        bbox_crops: Optional[List[np.ndarray]] = None,
        embeddings: Optional[List[np.ndarray]] = None,
        quality_mask: Optional[List[bool]] = None,
    ) -> None:
        """
        Args:
            bboxes_with_scores: (x, y, w, h, score) для каждой детекции.
            emotions_per_det: для каждой детекции — словарь
                {label, is_detected, probabilities} или None.
            timestamp: время кадра в секундах (для history).
            bbox_crops: вырезки лиц по bbox (опционально). Замораживается
                первый удачный кроп в track.image для миниатюры в HTML.
            embeddings: ArcFace-эмбеддинги по детекциям. Используются для
                ReID-стадии в ByteTrack — связки потерянных треков с
                новыми детекциями по cosine similarity.
            quality_mask: bool по детекциям. Эмбеддинг идёт в галерею
                трека только если True (хорошая поза, размер достаточный).
        """
        tracks, det_to_track_id = self._byte.update(
            bboxes_with_scores,
            embeddings=embeddings,
            quality_mask=quality_mask,
        )
        track_by_id = {t.id: t for t in self._byte._active + self._byte._lost}

        for det_idx, track_id in enumerate(det_to_track_id):
            if track_id < 0:
                continue
            t = track_by_id.get(track_id)
            if t is None or det_idx >= len(emotions_per_det):
                continue
            if t.image is None and bbox_crops is not None and det_idx < len(bbox_crops):
                crop = bbox_crops[det_idx]
                if crop is not None and crop.size > 0:
                    t.image = crop.copy()
            new_em = emotions_per_det[det_idx]
            if new_em is None:
                continue
            if t.emotion is None:
                t.emotion = {
                    'label': new_em['label'],
                    'is_detected': True,
                    'probabilities': dict(new_em['probabilities']),
                }
            else:
                a = self._alpha
                blended = {}
                for k, v in new_em['probabilities'].items():
                    prev = t.emotion['probabilities'].get(k, 0.0)
                    blended[k] = a * prev + (1.0 - a) * v
                top_label = max(blended, key=blended.get)
                t.emotion = {
                    'label': top_label,
                    'is_detected': True,
                    'probabilities': blended,
                }
            t.history.append({
                'timestamp': float(timestamp),
                'emotion': {
                    'label': t.emotion['label'],
                    'probabilities': dict(t.emotion['probabilities']),
                },
            })

    def predict(self) -> None:
        self._byte.predict()

    def get_tracks(self) -> List[STrack]:
        return self._byte.get_tracks()
