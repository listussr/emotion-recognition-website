# Docker-развёртывание

Полный стек (Redis + FastAPI + Celery worker + nginx с SPA) поднимается одной
командой через `docker compose`.

## 1. Подготовка моделей (один раз)

Runtime работает на ONNX. Перед сборкой конвертируем `.pth` в `.onnx`:

```bash
cd backend
python -m pip install torch onnx --upgrade
python scripts/convert_pth_to_onnx.py
```

В `backend/app/ml/models/` должны появиться:

- `convnext.onnx`
- `swin_tiny.onnx`
- `resnet50.onnx`
- `efficientnet_b3.onnx`

А также уже лежащие `w600k_mbf.onnx` (эмбеддер) и
`blaze_face_short_range.tflite` (детектор). Исходные `.pth` в образ не
попадают — см. `backend/.dockerignore`.

## 2. Сборка и запуск

Из корня репозитория:

```bash
docker compose up --build
```

После старта:

- Фронтенд: http://localhost:8080
- API (через nginx): http://localhost:8080/api/photo, /api/video
- Redis и прямой порт 8000 наружу не публикуются.

Остановка:

```bash
docker compose down
```

## 3. Переменные окружения

Все настройки `Settings` в `backend/app/config.py` переопределяются через env
(нижний регистр автоматически мапится в верхний Pydantic-settings):

| Переменная                   | Значение по умолчанию                 |
|------------------------------|---------------------------------------|
| `REDIS_URL`                  | `redis://redis:6379`                  |
| `MAX_FILE_SIZE_MB`           | `50`                                  |
| `MAX_VIDEO_DURATION_SEC`     | `30`                                  |
| `VIDEO_PROCESSING_TIMEOUT`   | `120`                                 |

Пример `.env` рядом с compose-файлом:

```
REDIS_URL=redis://redis:6379
MAX_FILE_SIZE_MB=80
```

И в `docker-compose.yml` для сервиса `backend` добавить `env_file: .env`.

## 4. Архитектура контейнеров

```
 ┌──────────┐      ┌──────────┐       ┌──────────┐
 │ browser  │─────>│ frontend │──────>│ backend  │
 │          │      │ (nginx)  │ /api/ │ (uvicorn)│
 └──────────┘      └──────────┘       └────┬─────┘
                                           │ Celery
                                           ▼
                                      ┌──────────┐       ┌──────────┐
                                      │   redis  │<──────│  worker  │
                                      └──────────┘       └──────────┘
```

- **frontend** (nginx) раздаёт собранный Vite-бандл и проксирует `/api/` на
  backend — поэтому CORS не нужен, всё same-origin.
- **backend** (FastAPI + uvicorn) принимает HTTP, кладёт задачи в Celery.
- **worker** выполняет тяжёлую ML-работу в отдельном процессе, не блокируя API.
- **redis** — брокер и result-backend Celery.

Backend и worker делят один образ (`emotion-backend:latest`): различаются
только `command`. Это ускоряет сборку (один `pip install`) и гарантирует
совпадение версий зависимостей.

## 5. Пересборка одного сервиса

```bash
docker compose build backend
docker compose up -d backend worker
```

(`worker` использует тот же image, поэтому пересобираем именно `backend`.)

## 6. Диагностика

```bash
# Логи воркера (видно профилирование и ошибки пайплайна):
docker compose logs -f worker

# Зайти внутрь backend:
docker compose exec backend /bin/bash

# Проверить, что ONNX-модели действительно лежат в образе:
docker compose exec backend ls -la app/ml/models
```

## 7. Production-заметки

- Текущая конфигурация — для dev/демо. Для продакшена стоит:
  - Зафиксировать версии пакетов в `requirements.txt` (сейчас без пинов).
  - Добавить healthcheck-и для `backend`/`worker`.
  - Поставить reverse-proxy с TLS перед nginx (или включить TLS в самом nginx).
  - Ограничить ресурсы в `deploy.resources` (CPU/RAM).
- `concurrency=2` у Celery подобран под 4-ядерную машину с 2 `intra_op_num_threads`
  у onnxruntime — см. комментарии в `emotion_classifier.py`.
