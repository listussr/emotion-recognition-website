from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import photo, video

app = FastAPI(title="Emotion recognizer", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(photo.router,  prefix="/api/photo")
app.include_router(video.router, prefix="/api/video")