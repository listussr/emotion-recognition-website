# Emotion AI

Веб-сервис распознавания эмоций по лицам на фотографиях и видео. Поддерживает четыре архитектуры классификаторов (ConvNeXt, Swin-Tiny, ResNet-50, EfficientNet-B3), детектирует и трекает несколько лиц одновременно, считает покадровую статистику эмоций по каждому человеку.

## Скриншот пайплайна

```
 ┌──────────┐      ┌──────────┐       ┌──────────┐
 │ browser  │─────▶│ frontend │──────▶│ backend  │
 │          │      │ (nginx)  │ /api/ │ (uvicorn)│
 └──────────┘      └──────────┘       └────┬─────┘
                                           │ Celery
                                           ▼
                                      ┌──────────┐       ┌──────────┐
                                      │  redis   │◀──────│  worker  │
                                      └──────────┘       └──────────┘
```

- **frontend** — React + Vite, собирается nginx'ом, проксирует `/api/` на backend (same-origin, без CORS).
- **backend** — FastAPI + uvicorn, валидирует запросы, кладёт задачи в Celery и ждёт результат.
- **worker** — Celery + ONNX Runtime + MediaPipe, гоняет ML-пайплайн.
- **redis** — брокер и result-backend Celery.

## Структура репозитория

```
emotion-recognition-website/
  backend/            # FastAPI API + Celery worker (см. backend/README.md)
  frontend/           # React + Vite SPA       (см. frontend/README.md)
  docker-compose.yml  # оркестрация всего стека
  Dockerfile          # (фронт/бек собираются из своих подкаталогов)
  DOCKER.md           # подробности по Docker-развёртыванию
  README.md           # этот файл
```

## Быстрый старт (Docker)

Требуется Docker Desktop (Windows/macOS) или docker engine + docker compose plugin (Linux).

### 1. Подготовить ONNX-модели

Один раз сконвертируй `.pth` (PyTorch) в `.onnx`:

```bash
cd backend
python -m pip install torch onnx efficientnet_pytorch --upgrade
python scripts/convert_pth_to_onnx.py
```

В `backend/app/ml/models/` появятся `convnext.onnx`, `swin_tiny.onnx`, `resnet50.onnx`, `efficientnet_b3.onnx`. Эмбеддер `w600k_mbf.onnx` и детектор `blaze_face_short_range.tflite` уже лежат в репозитории.

### 2. Поднять стек

Из корня репозитория:

```bash
docker compose up --build
```

После сборки (первый раз ~5–10 мин — apt + pip + node):

- Сайт: http://localhost:8080
- API через nginx: http://localhost:8080/api/photo, /api/video
- Redis и порт 8000 наружу не публикуются.

Остановка:

```bash
docker compose down
```

Полная очистка (включая том с временными аплоадами):

```bash
docker compose down -v
```

Подробности и тонкости — в [`DOCKER.md`](DOCKER.md).

## Деплой на сервер

Пошаговый план развёртывания на VPS (Ubuntu + Docker + Caddy с автоматическим
HTTPS) с чек-апами на каждом шаге — в [`DEPLOY.md`](DEPLOY.md). Продакшен-стек
поднимается прод-оверлеем:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Что умеет

- Принимает **фото** (jpg/jpeg/png, до 50 МБ) и **видео** (mp4/mov/avi, до 50 МБ и 30 сек).
- Выбирает модель классификатора через query-параметр `?model=convnext|swin|resnet_50|efficientnet_b3`.
- Возвращает аннотированное изображение/видео (с bbox'ами и метками эмоций) + таблицу вероятностей по каждому лицу.
- Для видео считает HTML-сводку (plotly): доля эмоций по времени для каждого устойчивого трека, общие метрики обработки.
- Идентифицирует лица между кадрами через ArcFace-эмбеддер + IoU-трекер с ReID, чтобы статистика по одному и тому же человеку не разваливалась на десятки треков.

## Локальная разработка (без Docker)

Backend и frontend поднимаются независимо. Подробности — в их README:

- [`backend/README.md`](backend/README.md) — Python 3.11, отдельно Redis.
- [`frontend/README.md`](frontend/README.md) — Node 18+, dev-сервер на 3000.

Минимально:

```bash
# терминал 1 — Redis
docker run --rm -p 6379:6379 redis:7-alpine

# терминал 2 — backend API
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload

# терминал 3 — Celery worker
cd backend
celery -A app.services.queue.celery_app worker --loglevel=info --pool=solo -Q celery

# терминал 4 — frontend
cd frontend && npm install && npm run dev
```

## Конфигурация

Настройки читаются pydantic-settings из переменных окружения. Самые ходовые перечислены в [`backend/README.md`](backend/README.md#конфигурация-env). В Docker переопределяются через `environment:` или `env_file:` в `docker-compose.yml`.

## Известные ограничения

- Контейнер CPU-only. На GPU перевод требует пересборки `onnxruntime-gpu` + проброса CUDA в Docker.
- Видео транскодируется в H.264 системным `ffmpeg` после OpenCV-записи в `mp4v` — это лишний проход по файлу. Альтернатива (pipe в ffmpeg-subprocess напрямую) не реализована.
- `--pool=solo` у Celery означает один таск за раз на один контейнер. Для параллелизма поднимай несколько `worker`-реплик в compose.
- Версии в `requirements.txt` не пиннуты — для прода стоит зафиксировать.

## Лицензия

См. [`LICENSE`](LICENSE).
