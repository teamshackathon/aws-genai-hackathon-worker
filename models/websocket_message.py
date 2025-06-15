from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    """
    WebSocket message schema for recipe generation task updates
    """
    type: str  # task_started, task_progress, task_completed, task_failed
    data: dict[str, Any]  # Task-specific data
    session_id: str  # Session identifier
    timestamp: datetime  # Message timestamp
    
    @classmethod
    def task_started(cls, session_id: str, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task started message"""
        return cls(
            type="task_started",
            data=data or {},
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def task_progress(cls, session_id: str, progress: float, message: str = "", data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task progress message"""
        progress_data = {
            "progress": progress,
            "message": message,
            **(data or {})
        }
        return cls(
            type="task_progress",
            data=progress_data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def task_completed(cls, session_id: str, result: Any, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task completed message"""
        completion_data = {
            "result": result,
            **(data or {})
        }
        return cls(
            type="task_completed",
            data=completion_data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def task_failed(cls, session_id: str, error: str, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task failed message"""
        error_data = {
            "error": error,
            **(data or {})
        }
        return cls(
            type="task_failed",
            data=error_data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
