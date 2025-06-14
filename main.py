import logging

from tasks import general

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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

    print("\nタスクがキューに追加されました。Workerで処理されます。")
    print("結果を確認するにはタスクIDを使用してください。")


if __name__ == "__main__":
    main()
