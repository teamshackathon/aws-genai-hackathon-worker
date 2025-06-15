from celery import Celery

from config import settings

# Celeryアプリケーションの初期化
app = Celery(
    "bae-recipe-worker",
    broker=settings.CELERY_BROCKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.queue_processor"]
)

# Celery設定
app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    result_expires=settings.CELERY_RESULT_EXPIRES,      task_routes={
        "tasks.queue_processor.*": {"queue": "recipe_gen_queue"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Beat スケジュール設定 - FastAPIからのキュー確認用
    beat_schedule={
        'scan-recipe-tasks': {
            'task': 'tasks.queue_processor.scan_recipe_tasks',
            'schedule': 300.0,  # 300秒ごとにFastAPIからのタスクがあるかスキャン
        },
    },
)

# Celeryアプリケーションを自動検出
app.autodiscover_tasks()


if __name__ == "__main__":
    app.start()