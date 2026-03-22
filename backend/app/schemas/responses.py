from pydantic import BaseModel, Field
from typing import Dict, List
import time

class Emotion(BaseModel):
    """
    Предсказанная эмоция.
    ---

    Поля:
     - _label_ - метка наиболее вероятной эмоции.
     - _probabilities_ - словарь эмоций с вероятностями.
    """
    label: str = Field(default="Undefined", min_length=3, max_length=20)
    probabilities: Dict[str, float] = Field(
        default_factory=lambda: {
            "anger": 0.0,
            "disgust": 0.0,
            "fear": 0.0,
            "happy": 0.0,
            "sad": 0.0,
            "surprise": 0.0,
            "neutral": 0.0,
            "contempt": 0.0,
        }
    )
    is_detected: bool = Field(default=False)

class PhotoResponse(BaseModel):
    """
    Результат предсказания для конкретного изображения.
    ---

    Поддерживает множество лиц на изображении.

    Поля:
     - _faces_num_ - количество лиц на изображении.
     - _emotions_ - словарь эмоций {'идентификатор лица': 'Объект эмоции'}
     - _process_time_ - время обработки кадра.
     - _result_image_ - байтовое изображение резльутата.
    """
    faces_num: int = Field(default=0, ge=0)
    emotions: Dict[str, Emotion] = Field(default_factory=dict)
    process_time: float = Field(default=0., ge=0.)
    result_image: str = Field(default="")

class FrameData(BaseModel):
    """
    Данные конкретного кадра.
    ---

    Поля:
     - _frame_timestamp_ - временная метка кадра.
     - _frame_response_ - объект результата предсказания кадра (PhotoResponse).
    """
    frame_timestamp: float = Field(default=0., ge=0.)
    frame_response: PhotoResponse = Field(default_factory=PhotoResponse)

class VideoResponse(BaseModel):
    """
    Результат предсказаний для всего видеопотока.
    ---

    Поля:
     - _processing_fps_ - частота кадров обработки.
     - _response_ - Массив объектов предсказаний каждого кадра (FrameData).
    """
    processing_fps: float = Field(default=0., ge=0.)
    duration_sec: float = Field(default=0.0, ge=0.0)
    total_frames_processed: int = Field(default=0, ge=0)
    result_video: str = Field(default="")
