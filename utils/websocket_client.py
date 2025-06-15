import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

from models.websocket_message import WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    WebSocket client for sending recipe generation task updates
    """
    
    def __init__(self, ws_url: str, timeout: float = 10.0):
        self.ws_url = ws_url
        self.timeout = timeout
    
    @asynccontextmanager
    async def connect(self):
        """
        Async context manager for WebSocket connection
        """
        websocket = None
        try:
            logger.info(f"Connecting to WebSocket: {self.ws_url}")
            websocket = await asyncio.wait_for(
                websockets.connect(self.ws_url),
                timeout=self.timeout
            )
            logger.info("WebSocket connection established")
            yield websocket
        except asyncio.TimeoutError:
            logger.error(f"WebSocket connection timeout after {self.timeout}s")
            raise
        except InvalidURI:
            logger.error(f"Invalid WebSocket URI: {self.ws_url}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise
        finally:
            if websocket:
                try:
                    await websocket.close()
                    logger.info("WebSocket connection closed")
                except Exception as e:
                    logger.warning(f"Error closing WebSocket: {e}")
    
    async def send_message(self, message: WebSocketMessage) -> bool:
        """
        Send a message via WebSocket
        
        Args:
            message: WebSocketMessage instance to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            async with self.connect() as websocket:
                message_json = message.model_dump_json()
                logger.debug(f"Sending WebSocket message: {message_json}")
                
                await websocket.send(message_json)
                logger.info(f"Successfully sent {message.type} message for session {message.session_id}")
                return True
                
        except ConnectionClosed:
            logger.error("WebSocket connection was closed unexpectedly")
            return False
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            return False
    
    def send_message_sync(self, message: WebSocketMessage) -> bool:
        """
        Synchronous wrapper for sending messages
        
        Args:
            message: WebSocketMessage instance to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Create new event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.send_message(message))
            
        except Exception as e:
            logger.error(f"Error in synchronous WebSocket send: {e}")
            return False
    
    async def send_task_started(self, session_id: str, data: Optional[dict] = None) -> bool:
        """Send task started notification"""
        message = WebSocketMessage.task_started(session_id, data)
        return await self.send_message(message)
    
    async def send_task_progress(self, session_id: str, progress: float, message_text: str = "", data: Optional[dict] = None) -> bool:
        """Send task progress notification"""
        message = WebSocketMessage.task_progress(session_id, progress, message_text, data)
        return await self.send_message(message)
    
    async def send_task_completed(self, session_id: str, result, data: Optional[dict] = None) -> bool:
        """Send task completed notification"""
        message = WebSocketMessage.task_completed(session_id, result, data)
        return await self.send_message(message)
    
    async def send_task_failed(self, session_id: str, error: str, data: Optional[dict] = None) -> bool:
        """Send task failed notification"""
        message = WebSocketMessage.task_failed(session_id, error, data)
        return await self.send_message(message)


# Synchronous wrapper functions for use in Celery tasks
def send_task_started_sync(ws_url: str, session_id: str, data: Optional[dict] = None) -> bool:
    """Synchronous wrapper for sending task started notification"""
    client = WebSocketClient(ws_url)
    message = WebSocketMessage.task_started(session_id, data)
    return client.send_message_sync(message)


def send_task_progress_sync(ws_url: str, session_id: str, progress: float, message_text: str = "", data: Optional[dict] = None) -> bool:
    """Synchronous wrapper for sending task progress notification"""
    client = WebSocketClient(ws_url)
    message = WebSocketMessage.task_progress(session_id, progress, message_text, data)
    return client.send_message_sync(message)


def send_task_completed_sync(ws_url: str, session_id: str, result, data: Optional[dict] = None) -> bool:
    """Synchronous wrapper for sending task completed notification"""
    client = WebSocketClient(ws_url)
    message = WebSocketMessage.task_completed(session_id, result, data)
    return client.send_message_sync(message)


def send_task_failed_sync(ws_url: str, session_id: str, error: str, data: Optional[dict] = None) -> bool:
    """Synchronous wrapper for sending task failed notification"""
    client = WebSocketClient(ws_url)
    message = WebSocketMessage.task_failed(session_id, error, data)
    return client.send_message_sync(message)
