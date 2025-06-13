from celery import Celery
from config import settings

# Celeryアプリケーションの初期化
app = Celery(
    "aws-genai-hackathon-worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks.general", "tasks.ai_processing", "tasks.data_processing"]
)

# Celery設定
app.conf.update(
    task_serializer=settings.celery_task_serializer,
    accept_content=settings.celery_accept_content,
    result_serializer=settings.celery_result_serializer,
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    result_expires=settings.celery_result_expires,
    task_routes={
        "tasks.ai_processing.*": {"queue": "ai_queue"},
        "tasks.data_processing.*": {"queue": "data_queue"},
        "tasks.general.*": {"queue": "general_queue"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Celeryアプリケーションを自動検出
app.autodiscover_tasks()


if __name__ == "__main__":
    app.start()
