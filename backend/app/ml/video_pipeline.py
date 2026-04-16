import cv2
import base64
import tempfile
import os
import time
import queue
import threading
import numpy as np
from collections import defaultdict
from typing import Dict, List, Literal, Optional

# отладочная информация
_PROFILE = os.environ.get('PIPELINE_PROFILE', '0') == '1'

from app.config import settings
from app.ml.tracker import Tracker
from app.ml.visualizer import annotate_frame
from app.ml.visualizer import LEGEND_WIDTH
from app.ml.image_pipeline import pipeline_image
from app.ml.face_embedder import FaceEmbedder
from app.ml.face_align import align_face, pose_quality, ARCFACE_SIZE
from app.ml.statistics import build_emotion_html

class VideoPipeline(object):
    """
    Пайплайн обработки и аннотации видео.
    ---
    """
    def __init__(self):
        """
        Пайплайн обработки и аннотации видео.
        ---
        """
        self._step = settings.video_classification_frequency
        self._embedder = FaceEmbedder()

    def _get_tracker(self) -> Tracker:
        """
        Инициализация трекера.
        ---
        """
        return Tracker(
            iou_threshold=settings.tracker_iou_threshold,
            track_ttl=settings.track_ttl,
            step=settings.tracker_step,
            reid_threshold=settings.reid_similarity_active,
            reid_threshold_gallery=settings.reid_similarity_gallery,
            embedding_store_threshold=settings.embedding_store_threshold,
            embeddings_count=settings.embeddings_count,
            confirmation_threshold=settings.confirmation_threshold,
            emotion_ema_alpha=settings.emotion_ema_alpha,
        )

    def _process_frame(self, frame: np.ndarray, frame_idx: int, tracker: Tracker, model: str, timestamp: float = 0.0,
                       prof: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Обработка и аннотация отдельного кадра.
        ---

        Особенности анализа.
         1) Анализируется только каждый `k`-ый кадр.
         2) На остальных `k-1` кадрах границы лиц предсказываются трекером.

        Конвейер идентификации на детекционном кадре:
         * 1: для каждой детекции берём 6 landmarks от MediaPipe и выравниваем
               лицо к шаблону ArcFace (112x112). Выровненный кроп подаётся в эмбеддер.
         * 2: по тем же landmarks считаем грубую оценку позы; если yaw/roll/размер
               вне допусков — эмбеддинг не используется (в tracker.update идёт None).
               Лицо при этом всё равно трекается по IoU.
         * 3: для эмоций используется исходный bbox-кроп, не выровненное лицо.
        """
        if frame_idx % self._step == 0:
            result, detections = pipeline_image.predict(frame, model, use_pass_pace_filter=False, prof=prof)

            valid_bboxes: List = []
            bbox_faces: List[np.ndarray] = []
            aligned_faces: List[np.ndarray] = []
            quality_mask: List[bool] = []

            frame_h, frame_w = frame.shape[:2]

            for det in detections:
                x, y, w, h = int(det[0]), int(det[1]), int(det[2]), int(det[3])
                kps = det[5] if len(det) > 5 else []

                x = max(0, x)
                y = max(0, y)
                w = min(w, frame_w - x)
                h = min(h, frame_h - y)

                bbox_crop = frame[y:y + h, x:x + w]
                if bbox_crop.size == 0:
                    continue

                # выровнивание
                aligned = align_face(frame, kps) if kps else None
                if aligned is None:
                    aligned = cv2.resize(bbox_crop, (ARCFACE_SIZE, ARCFACE_SIZE), interpolation=cv2.INTER_LINEAR)
                    good = False
                else:
                    good, _ = pose_quality(
                        kps, (w, h),
                        yaw_max=settings.pose_yaw_max,
                        roll_max_deg=settings.pose_roll_max,
                        min_face_px=settings.pose_min_face_px,
                    )

                valid_bboxes.append((x, y, w, h))
                bbox_faces.append(bbox_crop)
                aligned_faces.append(aligned)
                quality_mask.append(bool(good))

            # Эмбеддим все выровненные лица
            if aligned_faces:
                t0 = time.perf_counter() if prof is not None else 0.0
                raw_embeddings = self._embedder.encode(aligned_faces)
                if prof is not None:
                    prof['embed'] += time.perf_counter() - t0
                # низкокачественные лица подаются как None и трекаются по IoU,
                # но не участвуют в ReID-матчинге и не попадают в буфер треков.
                embeddings: List[Optional[np.ndarray]] = [
                    (raw_embeddings[i] if quality_mask[i] else None)
                    for i in range(len(aligned_faces))
                ]
            else:
                embeddings = []

            t0 = time.perf_counter() if prof is not None else 0.0
            tracker.update(valid_bboxes, result['emotions'], bbox_faces, embeddings, timestamp)
            if prof is not None:
                prof['tracker'] += time.perf_counter() - t0
        else:
            t0 = time.perf_counter() if prof is not None else 0.0
            tracker.predict()
            if prof is not None:
                prof['tracker'] += time.perf_counter() - t0

        tracks = tracker.get_tracks()
        emotions = {f'face_{i}': t.emotion for i, t in enumerate(tracks)}
        bboxes_for_draw = [(t.bbox[0], t.bbox[1], t.bbox[2], t.bbox[3], 1.0) for t in tracks]

        t0 = time.perf_counter() if prof is not None else 0.0
        annotated = annotate_frame(frame, bboxes_for_draw, emotions)
        if prof is not None:
            prof['annotate'] += time.perf_counter() - t0
        return annotated

    def process(self, tmp_file_path: str, model: Literal['convnext', 'swin', 'se_resnet'] = 'convnext') -> Dict:
        """
        Обротка и аннотирование видеопотока.
        ---

        Полная обработка осуществляется раз в `k` кадров.

        Остальные `k-1` кадров сохраняют эмоции с `1-ого` кадра. Границы лиц на них двигаются с помощью предсказаний трекера.

        Args:
            tmp_file_path (str): Путь к временному видео.
            model (Literal[&#39;convnext&#39;, &#39;swin&#39;, &#39;se_resnet&#39;], optional): Название модели для обработки. Defaults to 'convnext'.

        Raises:
            ValueError: Ошибка открытия файла.
            ValueError: Превышение длительности видео.

        Returns:
            Dict: Словарь для возврата ответа пользователю.
        """
        cap = cv2.VideoCapture(tmp_file_path)

        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видео: {tmp_file_path}")

        video_fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / video_fps
        frame_w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        session_tracks = {}

        if duration_sec > settings.max_video_duration_sec:
            cap.release()
            raise ValueError(
                f"Видео слишком длинное: {duration_sec:.1f} сек. "
                f"Максимум: {settings.max_video_duration_sec} сек."
            )

        output_path = tempfile.mktemp(suffix='.mp4')

        size = (frame_w + LEGEND_WIDTH, frame_h)
        writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'avc1'), video_fps, size)
        if not writer.isOpened():
            writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), video_fps, size)

        tracker = self._get_tracker()
        frame_idx = 0
        processed_frames = 0
        start_time = time.time()

        prof: Optional[Dict[str, float]] = defaultdict(float) if _PROFILE else None
        if _PROFILE:
            print(f"[PROFILE] source: {frame_w}x{frame_h} @ {video_fps:.1f}fps, {total_frames} frames, "
                  f"step={self._step}, detection_max_short_side={settings.detection_max_short_side}")

        frame_q: 'queue.Queue[Optional[tuple]]' = queue.Queue(maxsize=2)
        producer_exc: List[BaseException] = []

        def _producer():
            try:
                while True:
                    t0 = time.perf_counter() if prof is not None else 0.0
                    ret, frame = cap.read()
                    if prof is not None:
                        prof['decode'] += time.perf_counter() - t0
                    if not ret:
                        frame_q.put(None)
                        return
                    ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    frame_q.put((frame, ts))
            except BaseException as e:
                producer_exc.append(e)
                frame_q.put(None)

        producer_thread = threading.Thread(target=_producer, name='frame-decoder', daemon=True)
        producer_thread.start()

        try:
            while True:
                item = frame_q.get()
                if item is None:
                    break
                frame, timestamp = item

                annotated = self._process_frame(frame, frame_idx, tracker, model, timestamp, prof=prof)

                t0 = time.perf_counter() if prof is not None else 0.0
                writer.write(annotated)
                if prof is not None:
                    prof['write'] += time.perf_counter() - t0

                for track in tracker.get_tracks():
                    if track.history:
                        session_tracks[track.id] = track

                if frame_idx % self._step == 0:
                    processed_frames += 1

                frame_idx += 1
        finally:
            producer_thread.join(timeout=2.0)
            cap.release()
            writer.release()
            if producer_exc:
                raise producer_exc[0]

        total_time = time.time() - start_time
        processing_fps = round(processed_frames / total_time, 2) if total_time > 0 else 0.0

        if prof is not None:
            print(f"[PROFILE] total wall time: {total_time:.2f}s over {frame_idx} source frames "
                  f"({processed_frames} detection frames)")
            for k in ('decode', 'detect', 'emotion', 'embed', 'tracker', 'annotate', 'write'):
                v = prof.get(k, 0.0)
                pct = 100.0 * v / total_time if total_time > 0 else 0.0
                print(f"  {k:>16s}: {v:7.2f}s  ({pct:5.1f}%)")

        with open(output_path, 'rb') as f:
            video_bytes = f.read()
        os.remove(output_path)

        tracks = list(session_tracks.values())
        statistics_html = build_emotion_html(tracks)

        return {
            'processing_fps': processing_fps,
            'duration_sec': round(duration_sec, 2),
            'total_frames_processed': processed_frames,
            'result_video': base64.b64encode(video_bytes).decode('utf-8'),
            'statistics_html': statistics_html,
            '_tracks': tracks
        }

pipeline_video = VideoPipeline()
