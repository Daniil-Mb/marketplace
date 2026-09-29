from celery import Celery

from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "marketplace",
    broker=settings.rabbitmq_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_enable_remote_control=False,
)

celery_app.autodiscover_tasks(
    [
        "src.auth",
    ],
)
