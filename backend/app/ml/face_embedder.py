import os
import cv2
import numpy as np
import onnxruntime as ort
from app.config import settings

_MEAN = np.array([0.5, 0.5, 0.5], dtype=np.float32)
_STD  = np.array([0.5, 0.5, 0.5], dtype=np.float32)

_CPU = os.cpu_count() or 4
_INTRA_THREADS = max(1, min(8, _CPU))

class FaceEmbedder(object):
    """
    Распознаватель эмоций с использованием CPU.
    ---
    """
    def __init__(self):
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_options.intra_op_num_threads = _INTRA_THREADS
        sess_options.log_severity_level = 3

        model_path = settings.model_path_embedder
        if settings.use_quantized_models:
            base, ext = os.path.splitext(model_path)
            int8_path = f"{base}_int8{ext}"
            if os.path.exists(int8_path):
                print(f"[FaceEmbedder] using INT8 model: {int8_path}")
                model_path = int8_path
        self._session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        self._input_name = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name

    def encode(self, images: list[np.ndarray]) -> np.ndarray:
        """
        Декодирование батча изображений.
        ---

        Args:
            images: список кропов лиц в BGR

        Returns:
            np.ndarray: массив эмбеддингов переданных лиц.
        """
        if not images:
            return np.empty((0, 512), dtype=np.float32)

        batch = []
        for image in images:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (112, 112), interpolation=cv2.INTER_LINEAR)
            img = img.astype(np.float32) / 255.0
            img = (img - _MEAN) / _STD
            img = img.transpose(2, 0, 1)
            batch.append(img)

        batch = np.stack(batch, axis=0)

        embeddings = self._session.run([self._output_name], {self._input_name: batch})[0]

        embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-6)
        return embeddings
