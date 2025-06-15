"""
Redis の task:recipe_gen_* キーを監視してシンプルにprintする処理
"""
import logging
from datetime import datetime
from typing import Dict, List

import redis

from celery_app import app
from config import settings

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
async def process_recipe_generation_task(self, session_id: str, url: str, user_id: int, metadata: Dict = None):
    """FastAPIから呼び出されるレシピ生成タスク - argsでsession_id, url, user_id、kwargsでmetadataを受け取る"""
    try:
        print("\n=== Recipe Generation Task ===")
        print(f"Celery Task ID: {self.request.id}")
        print(f"Session ID: {session_id}")
        print(f"URL: {url}")
        print(f"User ID: {user_id}")
        print(f"Queue: {self.request.delivery_info.get('routing_key', 'unknown')}")
        print(f"Started at: {datetime.utcnow().isoformat()}")
        
        # メタデータがある場合は表示
        if metadata:
            print(f"Metadata: {metadata}")
            print(f"Priority: {metadata.get('priority', 'N/A')}")
            print(f"Created at: {metadata.get('created_at', 'N/A')}")
            print(f"Status: {metadata.get('status', 'N/A')}")
        

        
        # 処理結果
        result = {
            "status": "completed",
            "session_id": session_id,
            "url": url,
            "user_id": user_id,
            "celery_task_id": self.request.id,
            "processed_at": datetime.utcnow().isoformat(),
            "message": "レシピ生成タスクが正常に処理されました"
        }
        
        print(f"Result: {result}")
        print("=" * 50)
        
        return result
        
    except Exception as e:
        logger.error(f"Recipe generation task error: {str(e)}")
        print(f"処理エラー: {str(e)}")
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
