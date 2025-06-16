"""
Redis の task:recipe_gen_* キーを監視してシンプルにprintする処理
WebSocket通信でリアルタイム進捗を送信
"""
import logging
from datetime import datetime
from typing import Dict, List

import redis

from celery_app import app
from config import settings
from llm.gemini import GeminiService
from utils.llm import transform_recipe_data
from utils.websocket_client import send_task_completed_sync, send_task_failed_sync, send_task_progress_sync, send_task_started_sync

logger = logging.getLogger(__name__)


class SimpleQueueProcessor:
    """Redis task キーを監視・処理するシンプルなクラス"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def find_recipe_tasks(self) -> List[Dict]:
        """task:recipe_gen_* パターンのキーを検索"""
        try:
            # recipe_gen で始まるタスクキーを検索
            task_keys = self.redis_client.keys("task:recipe_gen_*")
            tasks = []
            
            for task_key in task_keys:
                # Redisハッシュからデータを取得
                task_data = self.redis_client.hgetall(task_key)
                if task_data:
                    tasks.append({
                        "key": task_key,
                        "data": task_data
                    })
            
            return tasks
            
        except Exception as e:
            logger.error(f"タスク検索エラー: {str(e)}")
            return []


@app.task(bind=True, name='tasks.queue_processor.process_recipe_generation_task')
def process_recipe_generation_task(self, session_id: str, url: str, user_id: int, metadata: Dict = None):
    """FastAPIから呼び出されるレシピ生成タスク - WebSocket通信でリアルタイム進捗を送信"""
    ws_url = settings.WEBSOCKET_URL + f"?session_id={session_id}"
    
    try:
        print("\n=== Recipe Generation Task Started ===")
        print(f"Session ID: {session_id}")
        print(f"URL: {url}")
        print(f"User ID: {user_id}")
        print(f"Queue: {self.request.delivery_info.get('routing_key', 'unknown')}")
        print(f"Started at: {datetime.utcnow().isoformat()}")
        
        # WebSocket: タスク開始通知
        task_start_data = {
            "url": url,
            "user_id": user_id,
            "queue": self.request.delivery_info.get('routing_key', 'unknown')
        }
        
        ws_sent = send_task_started_sync(ws_url, session_id, task_start_data)
        print(f"WebSocket task started notification sent: {ws_sent}")
        
        # メタデータがある場合は表示
        if metadata:
            print(f"Metadata: {metadata}")
            print(f"Priority: {metadata.get('priority', 'N/A')}")
            print(f"Created at: {metadata.get('created_at', 'N/A')}")
            print(f"Status: {metadata.get('status', 'N/A')}")
        
        # ここでレシピ生成の実処理をシミュレート（段階的に進捗を送信）
        
        # Step 1: レシピ生成開始
        print("Step 1: レシピ生成開始")
        gemini_service = GeminiService()
        result = gemini_service.generate_content(url)
        
        transform_result = transform_recipe_data(result, url, user_id)

        # Step 2: レシピ生成完了
        print("Step 2: レシピ生成完了")
        progress_data = {"step": "recipe_generation", "status": "completed", "content": "生成されたレシピ情報を整理中"}
        send_task_progress_sync(ws_url, session_id, 100.0, "レシピ生成完了！", progress_data)
        
        
        # WebSocket: タスク完了通知
        completion_data = {
            "processing_time_seconds": 5,  # シミュレート処理時間
            "steps_completed": 4,
            "content": "レシピ生成が完了しました",
        }
        send_task_completed_sync(ws_url, session_id, transform_result, completion_data)
        
        print(f"Result: {transform_result}")
        print("=" * 50)
        
        return transform_result
        
    except Exception as e:
        logger.error(f"Recipe generation task error: {str(e)}")
        print(f"処理エラー: {str(e)}")
        
        # WebSocket: タスク失敗通知
        error_data = {
            "error_type": type(e).__name__,
            "failed_at": datetime.utcnow().isoformat()
        }
        send_task_failed_sync(ws_url, session_id, str(e), error_data)
        
        raise


@app.task(bind=True, name='tasks.queue_processor.scan_recipe_tasks')
def scan_recipe_tasks(self):
    """FastAPIからのキュー確認用 - recipe_gen タスクをスキャンしてprintする"""
    try:
        processor = SimpleQueueProcessor()
        tasks = processor.find_recipe_tasks()
        
        print("\n=== FastAPI Queue Scan Results ===")
        print(f"発見されたタスク数: {len(tasks)}")
        print(f"スキャン時刻: {datetime.utcnow().isoformat()}")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- Task {i} ---")
            print(f"Key: {task['key']}")
            print("Data:")
            for field, value in task['data'].items():
                print(f"  {field}: {value}")
        
        if not tasks:
            print("FastAPIからのタスクは見つかりませんでした。")
        
        print("=" * 40)
        
        logger.info(f"FastAPI queue scan completed: {len(tasks)} tasks found")
        
        return {
            "status": "SUCCESS",
            "tasks_found": len(tasks),
            "scan_time": datetime.utcnow().isoformat(),
            "message": f"FastAPIキューから{len(tasks)}個のタスクをスキャンしました"
        }
        
    except Exception as e:
        logger.error(f"FastAPI queue scan error: {str(e)}")
        print(f"エラーが発生しました: {str(e)}")
        raise
