import logging
from celery_app import app
from tasks import general, ai_processing, data_processing

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """メイン関数 - テスト用のタスク実行例"""
    logger.info("AWS GenAI Hackathon Workerを開始します")
    
    # テスト用のタスク実行例
    print("=== タスク実行例 ===")
    
    # 基本タスク
    result1 = general.add_numbers.delay(10, 20)
    print(f"数値計算タスク ID: {result1.id}")
    
    # テキスト処理
    result2 = general.process_text.delay("Hello World from Celery Worker!")
    print(f"テキスト処理タスク ID: {result2.id}")
    
    # AI処理
    result3 = ai_processing.analyze_sentiment.delay("This is a great day! I love working with Celery.")
    print(f"感情分析タスク ID: {result3.id}")
    
    # データ処理
    sample_data = [
        {"name": "alice", "age": "25", "city": "tokyo"},
        {"name": "bob", "age": "30", "city": "osaka"},
        {"name": "charlie", "age": "35", "city": "tokyo"}
    ]
    result4 = data_processing.process_csv_data.delay(sample_data)
    print(f"データ処理タスク ID: {result4.id}")
    
    print("\nタスクがキューに追加されました。Workerで処理されます。")
    print("結果を確認するにはタスクIDを使用してください。")


if __name__ == "__main__":
    main()