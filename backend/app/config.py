from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "Emotion recognizer"
    debug: bool = True
    max_file_size_mb: int = 50
    allowed_video_formats: List[str] = ['mp4', 'mov', 'avi']
    allowed_photo_formats: List[str] = ['jpg', 'jpeg', 'png']
    redis_url: str = 'redis://localhost:6379'

settings = Settings()