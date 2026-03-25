import cv2
import base64
import tempfile
import os
import time
import numpy as np
from typing import Dict, Literal

from app.config import settings
from app.ml.tracker import Tracker
from app.ml.visualizer import annotate_frame
from app.ml.visualizer import LEGEND_WIDTH
from app.ml.image_pipeline import pipeline_image
from app.ml.face_embedder import FaceEmbedder
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
        return Tracker(iou_threshold=settings.tracker_iou_threshold, track_ttl=settings.track_ttl, step=settings.tracker_step, reid_threshold=0.45)

    def _process_frame(self, frame: np.ndarray, frame_idx: int, tracker: Tracker, model: str, timestamp: float = 0.0) -> np.ndarray:
        """
        Обработка и аннотация отдельного кадра.
        --- 

        Особенности анализа.
         1) Анализируется только каждый `k`-ый кадр.
         2) На остальных `k-1` кадрах границы лиц предсказываются трекером.

        Args:
            frame (np.ndarray): Исходный кадрю
            frame_idx (int): Номер кадра для определения необходимости анализа.
            tracker (Tracker): Объект трекера.
            model (str): Название модели обработки.

        Returns:
            np.ndarray: Аннотированный кадр.
        """
        if frame_idx % self._step == 0:
            result, detections = pipeline_image.predict(frame, model, use_pass_pace_filter=False)
            bboxes = [d[:4] for d in detections]

            valid_bboxes = []
            faces = []

            for (x, y, w, h) in bboxes:
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)

                x = max(0, x)
                y = max(0, y)
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)

                crop = frame[y:y + h, x:x + w]

                if crop.size == 0:
                    continue

                valid_bboxes.append((x, y, w, h))
                faces.append(crop)

            if faces:
                embeddings = self._embedder.encode(faces)
            else:
                embeddings = np.empty((0, 512), dtype=np.float32)

            tracker.update(valid_bboxes, result['emotions'], faces, embeddings, timestamp)
        else:
            tracker.predict()

        tracks = tracker.get_tracks()
        emotions = {f'face_{i}': t.emotion for i, t in enumerate(tracks)}
        bboxes_for_draw = [(t.bbox[0], t.bbox[1], t.bbox[2], t.bbox[3], 1.0) for t in tracks]

        return annotate_frame(frame, bboxes_for_draw, emotions)

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
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        writer = cv2.VideoWriter(
            output_path, fourcc, video_fps,
            (frame_w + LEGEND_WIDTH, frame_h)
        )

        tracker = self._get_tracker()
        frame_idx = 0
        processed_frames = 0
        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                annotated = self._process_frame(frame, frame_idx, tracker, model, timestamp)
                writer.write(annotated)

                for track in tracker.get_tracks():
                    if track.history:
                        session_tracks[track.id] = track

                if frame_idx % self._step == 0:
                    processed_frames += 1

                frame_idx += 1
        finally:
            cap.release()
            writer.release()

        total_time = time.time() - start_time
        processing_fps = round(processed_frames / total_time, 2) if total_time > 0 else 0.0

        with open(output_path, 'rb') as f:
            video_bytes = f.read()
        os.remove(output_path)

        tracks = list(session_tracks.values())
        statistics_html = build_emotion_html(tracks, output_path="emotion_report.html")

        return {
            'processing_fps': processing_fps,
            'duration_sec': round(duration_sec, 2),
            'total_frames_processed': processed_frames,
            'result_video': base64.b64encode(video_bytes).decode('utf-8'),
            'statistics_html': statistics_html,
        }

pipeline_video = VideoPipeline()
