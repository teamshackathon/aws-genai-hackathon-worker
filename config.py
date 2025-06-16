import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Redis設定
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROCKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # WebSocket設定
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/api/v1/ws/recipe-gen/celery")
    
    # Celery設定
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TIMEZONE: str = "Asia/Tokyo"
    CELERY_ENABLE_UTC: bool = True
    CELERY_RESULT_EXPIRES: int = 3600

    # Beat schedule設定（Celery beatのスケジュールファイルのパス）
    BEAT_SCHEDULE_FILENAME: str = "/app/data/celerybeat-schedule"

    # LLM
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

settings = Settings()
