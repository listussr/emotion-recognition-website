from pydantic_settings import BaseSettings
from typing import Dict, List

class Settings(BaseSettings):
    app_name: str = "Emotion recognizer"
    debug: bool = True
    max_file_size_mb: int = 50
    allowed_video_formats: List[str] = ['mp4', 'mov', 'avi']
    allowed_photo_formats: List[str] = ['jpg', 'jpeg', 'png']
    redis_url: str = 'redis://localhost:6379'
    model_path_convnext: str = r'app\ml\models\convnext_gelu_head.onnx'
    model_path_swin: str = r'app\ml\models\swin_tiny.onnx'
    model_path_se_resnet: str = r'app\ml\models\resnet_18.onnx'
    model_path_embedder: str = r'app\ml\models\w600k_mbf.onnx'
    video_classification_frequency: int = 5
    tracker_iou_threshold: float = 0.18
    track_ttl: int = 12
    tracker_step: int = 7
    max_video_duration_sec: int = 30
    video_processing_timeout: int = 120
    detection_confidence: float = 0.6
    reid_similarity: float = 0.4
    embeddings_count: int = 15
    confirmation_threshold: int = 5

settings = Settings()
