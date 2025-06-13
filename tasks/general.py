import logging
import time

from celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def add_numbers(self, x: int, y: int) -> dict:
    """数値を足し算する基本的なタスク"""
    try:
        logger.info(f"タスク {self.request.id}: {x} + {y} を計算中...")
        
        # 進捗状況を更新
        self.update_state(state="PROGRESS", meta={"current": 50, "total": 100})
        time.sleep(2)  # 重い処理をシミュレート
        
        result = x + y
        logger.info(f"タスク {self.request.id}: 計算完了 = {result}")
        
        return {"status": "SUCCESS", "result": result, "message": f"{x} + {y} = {result}"}
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def process_text(self, text: str) -> dict:
    """テキスト処理タスク"""
    try:
        logger.info(f"タスク {self.request.id}: テキスト処理開始 - {text[:50]}...")
        
        # 進捗状況を更新
        self.update_state(state="PROGRESS", meta={"current": 25, "total": 100})
        time.sleep(1)
        
        # テキスト処理
        processed_text = text.upper().strip()
        
        self.update_state(state="PROGRESS", meta={"current": 75, "total": 100})
        time.sleep(1)
        
        word_count = len(processed_text.split())
        
        logger.info(f"タスク {self.request.id}: テキスト処理完了")
        
        return {
            "status": "SUCCESS",
            "original_text": text,
            "processed_text": processed_text,
            "word_count": word_count,
            "message": "テキスト処理が完了しました"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def health_check(self) -> dict:
    """ヘルスチェックタスク"""
    logger.info(f"タスク {self.request.id}: ヘルスチェック実行")
    return {
        "status": "SUCCESS",
        "message": "Worker is healthy",
        "timestamp": time.time(),
        "task_id": self.request.id
    }
