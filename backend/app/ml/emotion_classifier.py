import os
import cv2
import numpy as np
import onnxruntime as ort

_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# O3. Подбор числа потоков под машину. Не «жадничаем» (Celery worker и MediaPipe
# тоже хотят cpu-time): берём половину ядер, но не больше 4 — выше плато.
_CPU = os.cpu_count() or 4
_INTRA_THREADS = max(1, min(4, _CPU // 2))


class EmotionRecognizer(object):
    """
    Распознаватель эмоций с использованием CPU.
    ---
    """
    def __init__(self, model_path: str):
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        # O3. Эмоциональные модели (convnext/swin/resnet) — самые крупные в пайплайне.
        # ORT_PARALLEL + inter_op_num_threads=2 даёт прирост на больших графах,
        # intra_op_num_threads подгоняется по числу ядер (см. _INTRA_THREADS выше).
        sess_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
        sess_options.inter_op_num_threads = 2
        sess_options.intra_op_num_threads = _INTRA_THREADS
        self._session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        self._input_name = self._session.get_inputs()[0].name
    
    def predict(self, images: list[np.ndarray]) -> np.ndarray:
        """
        Args:
            images: список кропов лиц в BGR

        Returns:
            np.ndarray: массив вероятностей shape (N, num_classes)
        """
        if not images:
            return np.empty((0, 8), dtype=np.float32)
        batch = []
        for image in images:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_LINEAR)
            img = img.astype(np.float32) / 255.0
            img = (img - _MEAN) / _STD
            img = img.transpose(2, 0, 1)
            batch.append(img)

        batch = np.stack(batch, axis=0)

        logits = self._session.run(None, {self._input_name: batch})[0]

        e = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)
        return probs