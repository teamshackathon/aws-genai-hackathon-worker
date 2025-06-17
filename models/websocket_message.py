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
    def task_progress(cls, session_id: str, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task progress message"""
        return cls(
            type="task_progress",
            data=data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def task_completed(cls, session_id: str, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task completed message"""
        return cls(
            type="task_completed",
            data=data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def task_failed(cls, session_id: str, data: Optional[dict] = None) -> "WebSocketMessage":
        """Create a task failed message"""
        return cls(
            type="task_failed",
            data=data,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
