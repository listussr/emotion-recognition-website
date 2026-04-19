# Emotion AI — Backend

FastAPI-сервис распознавания эмоций по лицам на фото и видео. Тяжёлая ML-обработка вынесена в Celery-воркер, общающийся с API через Redis.

## Стек

- **FastAPI + uvicorn** — HTTP API.
- **Celery + Redis** — очередь задач и result-backend для асинхронной обработки.
- **MediaPipe (BlazeFace)** — детектор лиц.
- **ONNX Runtime** — инференс четырёх классификаторов эмоций (ConvNeXt, Swin-Tiny, ResNet-50, EfficientNet-B3) и эмбеддера ArcFace для ReID между кадрами.
- **OpenCV (headless) + ffmpeg** — декодирование/энкодинг видео, перекодировка результата в H.264 для браузера.

## Структура

```
backend/
  app/
    main.py              # FastAPI app, монтирование роутов
    config.py            # pydantic-settings: пути моделей, тайминги, пороги
    api/
      routes/
        photo.py         # POST /api/photo/  -> Celery task
        video.py         # POST /api/video/  -> Celery task
    schemas/             # pydantic-схемы запросов/ответов
    services/
      queue.py           # инициализация Celery (broker/backend = Redis)
    ml/
      face_detector.py   # обёртка над MediaPipe FaceDetector
      face_align.py      # выравнивание лица к ArcFace-шаблону по landmarks
      face_embedder.py   # ArcFace-эмбеддер (w600k_mbf.onnx)
      emotion_classifier.py  # обёртка над ONNX-классификаторами
      tracker.py         # IoU-трекер с ReID по эмбеддингам
      image_pipeline.py  # пайплайн фото
      video_pipeline.py  # пайплайн видео + транскод в H.264
      visualizer.py      # отрисовка bbox/легенды
      statistics.py      # plotly-сводка эмоций по трекам
      models/            # *.onnx и *.tflite артефакты
  worker/
    tasks.py             # process_image / process_video — Celery-таски
  scripts/
    convert_pth_to_onnx.py   # конвертация обученных .pth в .onnx
    model_classes.py         # пользовательские классы (CustomEfficientNetB3) для unpickle
  Dockerfile
  requirements.txt
```

## Запуск через Docker (рекомендуется)

Полный стек поднимается одной командой из корня репозитория:

```bash
docker compose up --build
```

Подробнее — в [`../DOCKER.md`](../DOCKER.md).

## Локальный запуск (без Docker)

Понадобятся Python 3.11, Redis и системный `ffmpeg`.

```bash
cd backend
python -m venv venv
venv\Scripts\activate              # Windows PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Запустить Redis отдельно (например, через docker run -p 6379:6379 redis:7-alpine).

# В одном терминале — API:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# В другом — Celery-воркер:
celery -A app.services.queue.celery_app worker --loglevel=info --pool=solo -Q celery
```

> `--pool=solo` обязателен: ONNX Runtime сессии и MediaPipe-граф создаются на импорте модуля, а форк дочерних процессов в дефолтном `prefork` ломает нативные хэндлы — таски виснут навечно.

## Подготовка моделей

В `app/ml/models/` должны лежать готовые ONNX:

- `convnext.onnx`
- `swin_tiny.onnx`
- `resnet50.onnx`
- `efficientnet_b3.onnx`
- `w600k_mbf.onnx` (эмбеддер ArcFace, есть в репозитории)
- `blaze_face_short_range.tflite` (детектор, есть в репозитории)

Конвертация из `.pth` (PyTorch) делается один раз скриптом:

```bash
python scripts/convert_pth_to_onnx.py
```

Скрипт ожидает рядом `app/ml/models/*.pth` и пишет соответствующие `.onnx`. Для `CustomEfficientNetB3` нужен файл с определением класса в `scripts/model_classes.py` (он уже есть в репозитории, тянет `efficientnet_pytorch` — поставь его локально перед запуском конвертации).

## API

Все эндпоинты возвращают JSON. Ошибки — стандартные HTTP-коды (415 — формат, 413 — размер, 504 — тайм-аут, 500 — внутренняя).

### `POST /api/photo/?model=<key>`

multipart/form-data с полем `file` (jpg/jpeg/png, ≤ 50 МБ).

Параметр `model`: `convnext` (по умолчанию) | `swin` | `resnet_50` | `efficientnet_b3`.

Ответ:

```json
{
  "faces_num": 2,
  "process_time": 0.42,
  "emotions": {
    "face_0": {
      "label": "happy",
      "is_detected": true,
      "probabilities": {"angry": 0.01, "happy": 0.87, ...}
    }
  },
  "result_image": "<base64 jpeg>"
}
```

### `POST /api/video/?model=<key>`

multipart/form-data с полем `file` (mp4/mov/avi, ≤ 50 МБ, ≤ 30 сек).

Ответ:

```json
{
  "processing_fps": 12.4,
  "duration_sec": 8.32,
  "total_frames_processed": 250,
  "result_video": "<base64 mp4 H.264>",
  "statistics_html": "<plotly html>"
}
```

## Конфигурация (env)

Все поля `Settings` из `app/config.py` переопределяются переменными окружения (нижний регистр маппится в верхний). Самое полезное:

| Переменная                 | Дефолт                  | Назначение                                                    |
|----------------------------|-------------------------|---------------------------------------------------------------|
| `REDIS_URL`                | `redis://localhost:6379`| Брокер и result-backend Celery.                                |
| `SHARED_TMP_DIR`           | `None`                  | Каталог для временных видео-аплоадов, общий между backend и worker. В Docker — `/shared-uploads`. |
| `MAX_FILE_SIZE_MB`         | `50`                    | Лимит размера загружаемого файла.                              |
| `MAX_VIDEO_DURATION_SEC`   | `30`                    | Лимит длительности видео.                                      |
| `VIDEO_PROCESSING_TIMEOUT` | `120`                   | Сколько ждём результат видео-таска от воркера.                  |
| `PHOTO_PROCESSING_TIMEOUT` | `120`                   | То же для фото (с запасом на cold start ONNX/MediaPipe).        |
| `PIPELINE_PROFILE`         | —                       | Если выставлено в `1`, воркер печатает профилировку фаз пайплайна. |

## Архитектурные заметки

- **Почему Celery, а не background-tasks FastAPI.** Видеообработка может занимать десятки секунд — держать её внутри HTTP-обработчика плохо для backpressure (uvicorn-воркер залипает) и для горизонтального скейла. Celery-воркер можно поднимать отдельно и в нескольких репликах.
- **Почему `--pool=solo`.** См. выше про fork-небезопасность ONNX Runtime / MediaPipe.
- **Почему транскод видео в H.264 в конце пайплайна.** OpenCV-wheel `opencv-python-headless` поставляется со встроенным FFmpeg без libx264 (лицензия), поэтому `VideoWriter` с fourcc `'avc1'` не открывается и пайплайн пишет в `'mp4v'` (MPEG-4 Part 2) — браузеры этот контейнер в `<video>` не воспроизводят. После записи прогоняем системный `ffmpeg -c:v libx264 -movflags +faststart`, чтобы видео играло без скачивания.
- **Почему общий volume `/shared-uploads`.** Backend пишет временный файл, передаёт воркеру **путь** через Celery; разные контейнеры не делят `/tmp`, поэтому нужен общий named-volume.

## Диагностика

```bash
# Логи воркера (видно профилировку и ошибки пайплайна):
docker compose logs -f worker

# Зайти внутрь backend:
docker compose exec backend /bin/bash

# Проверить, что ONNX-модели лежат в образе:
docker compose exec backend ls -la app/ml/models
```
