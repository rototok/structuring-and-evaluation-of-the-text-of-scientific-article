import os

from celery import Celery


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

celery = Celery(
    "backend",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=6000,            
)

celery.autodiscover_tasks(["app"])