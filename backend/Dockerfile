# syntax=docker/dockerfile:1.7

# ---- Backend (FastAPI + Celery worker) ----------------------------------
# Единый образ для API и Celery-воркера. Различие в команде запуска задаётся
# в docker-compose (см. сервисы `backend` и `worker`).
#
# База: python:3.11-slim — полноценный Debian со свежим libstdc++ (onnxruntime
# и mediapipe подтягивают C++-рантайм). slim даёт меньший образ, чем полная
# Debian.
#
# Сборка:
#   docker build -t emotion-backend ./backend
# Запуск API (локально, без compose):
#   docker run --rm -p 8000:8000 emotion-backend
FROM python:3.11-slim AS base


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libxcb1 \
        libgles2 \
        libegl1 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app


COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless \
    && pip install --no-cache-dir opencv-python-headless


COPY app ./app
COPY worker ./worker

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
