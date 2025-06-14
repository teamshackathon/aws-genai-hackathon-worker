from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Redis設定
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Celery設定
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: list = ["json"]
    celery_timezone: str = "Asia/Tokyo"
    celery_enable_utc: bool = True
    celery_result_expires: int = 3600


settings = Settings()
