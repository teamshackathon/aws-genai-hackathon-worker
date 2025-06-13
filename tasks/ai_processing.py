import time
import logging
from celery import current_task
from celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def analyze_sentiment(self, text: str) -> dict:
    """感情分析タスク（AI処理のシミュレーション）"""
    try:
        logger.info(f"タスク {self.request.id}: 感情分析開始")
        
        # AI処理をシミュレート
        self.update_state(state="PROGRESS", meta={"current": 20, "total": 100, "step": "前処理中..."})
        time.sleep(2)
        
        self.update_state(state="PROGRESS", meta={"current": 50, "total": 100, "step": "AIモデル実行中..."})
        time.sleep(3)
        
        self.update_state(state="PROGRESS", meta={"current": 80, "total": 100, "step": "結果処理中..."})
        time.sleep(1)
        
        # 簡単な感情分析のシミュレーション
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        logger.info(f"タスク {self.request.id}: 感情分析完了 - {sentiment}")
        
        return {
            "status": "SUCCESS",
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_words_found": positive_count,
            "negative_words_found": negative_count,
            "message": f"感情分析完了: {sentiment} (信頼度: {confidence:.2f})"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)


@app.task(bind=True)
def generate_summary(self, text: str, max_length: int = 100) -> dict:
    """テキスト要約タスク（AI処理のシミュレーション）"""
    try:
        logger.info(f"タスク {self.request.id}: テキスト要約開始")
        
        self.update_state(state="PROGRESS", meta={"current": 30, "total": 100, "step": "テキスト解析中..."})
        time.sleep(2)
        
        self.update_state(state="PROGRESS", meta={"current": 70, "total": 100, "step": "要約生成中..."})
        time.sleep(3)
        
        # 簡単な要約のシミュレーション
        sentences = text.split(". ")
        if len(sentences) > 3:
            summary = ". ".join(sentences[:3]) + "."
        else:
            summary = text
        
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        logger.info(f"タスク {self.request.id}: テキスト要約完了")
        
        return {
            "status": "SUCCESS",
            "original_text": text,
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text),
            "message": "テキスト要約が完了しました"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)
