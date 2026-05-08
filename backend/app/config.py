from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Emotion recognizer"
    debug: bool = True
    max_file_size_mb: int = 50
    allowed_video_formats: List[str] = ['mp4', 'mov', 'avi']
    allowed_photo_formats: List[str] = ['jpg', 'jpeg', 'png']

    redis_url: str = 'redis://localhost:6379'

    shared_tmp_dir: str | None = None

    model_path_convnext:        str = 'app/ml/models/convnext.onnx'
    model_path_swin:            str = 'app/ml/models/swin_tiny.onnx'
    model_path_resnet_50:       str = 'app/ml/models/resnet50.onnx'
    model_path_efficientnet_b3: str = 'app/ml/models/efficientnet_b3.onnx'
    model_path_embedder:        str = 'app/ml/models/w600k_mbf.onnx'

    model_input_size_convnext:        int = 224
    model_input_size_swin:            int = 224
    model_input_size_resnet_50:       int = 224
    model_input_size_efficientnet_b3: int = 300

    video_classification_frequency: int = 8
    tracker_iou_threshold: float = 0.18
    track_ttl: int = 6
    tracker_step: int = 7
    max_video_duration_sec: int = 30
    video_processing_timeout: int = 120

    photo_processing_timeout: int = 120
    detection_confidence: float = 0.6
    detection_max_short_side: int = 480
    embed_skip_single_face: bool = True
    use_quantized_models: bool = False
    processing_max_short_side: int = 720
    video_frame_decimation: int = 2
    bbox_smoothing_alpha: float = 0.9

    bytetrack_track_thresh: float = 0.5
    bytetrack_match_thresh: float = 0.4
    bytetrack_track_buffer: int = 360
    bytetrack_new_track_thresh: float = 0.6
    bytetrack_min_hits_to_confirm: int = 2


    bytetrack_reid_threshold: float = 0.3
    bytetrack_gallery_size: int = 15
    emotion_ema_alpha: float = 0.75
    reid_similarity_active: float = 0.37
    reid_similarity_gallery: float = 0.42
    embedding_store_threshold: float = 0.42
    embeddings_count: int = 15
    confirmation_threshold: int = 5
    pose_yaw_max: float = 0.25
    pose_roll_max: float = 20.0
    pose_min_face_px: int = 60

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
