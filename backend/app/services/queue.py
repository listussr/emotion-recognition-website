from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url + "/0",
    backend=settings.redis_url + "/1",
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_routes={"worker.tasks.*": {"queue": "celery"}},
)
