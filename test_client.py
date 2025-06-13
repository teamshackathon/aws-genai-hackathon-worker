"""
Celeryタスクをテストするためのクライアントスクリプト
"""
from tasks import ai_processing, data_processing, general


def test_general_tasks():
    """基本タスクのテスト"""
    print("=== 基本タスクのテスト ===")
    
    # 数値計算
    result1 = general.add_numbers.delay(15, 25)
    print(f"数値計算タスク: {result1.id}")
    
    # テキスト処理
    result2 = general.process_text.delay("hello world from celery test")
    print(f"テキスト処理タスク: {result2.id}")
    
    # ヘルスチェック
    result3 = general.health_check.delay()
    print(f"ヘルスチェックタスク: {result3.id}")
    
    return [result1, result2, result3]


def test_ai_tasks():
    """AI処理タスクのテスト"""
    print("\n=== AI処理タスクのテスト ===")
    
    # 感情分析
    result1 = ai_processing.analyze_sentiment.delay(
        "I absolutely love working with Celery! It's fantastic and makes my life so much easier."
    )
    print(f"感情分析タスク: {result1.id}")
    
    # テキスト要約
    long_text = """
    Celery is a distributed task queue system for Python that allows you to run tasks asynchronously.
    It's particularly useful for handling time-consuming operations that don't need to block the main application.
    With Celery, you can distribute work across multiple workers and even multiple machines.
    The system supports various message brokers including Redis, RabbitMQ, and Amazon SQS.
    It also provides monitoring tools like Flower to track task execution and worker status.
    """
    result2 = ai_processing.generate_summary.delay(long_text.strip(), 150)
    print(f"テキスト要約タスク: {result2.id}")
    
    return [result1, result2]


def test_data_tasks():
    """データ処理タスクのテスト"""
    print("\n=== データ処理タスクのテスト ===")
    
    # CSVデータ処理
    sample_data = [
        {"name": "alice", "age": "28", "city": "tokyo", "department": "engineering"},
        {"name": "bob", "age": "32", "city": "osaka", "department": "marketing"},
        {"name": "charlie", "age": "25", "city": "tokyo", "department": "engineering"},
        {"name": "diana", "age": "29", "city": "kyoto", "department": "design"},
        {"name": "eve", "age": "31", "city": "tokyo", "department": "marketing"}
    ]
    result1 = data_processing.process_csv_data.delay(sample_data)
    print(f"CSVデータ処理タスク: {result1.id}")
    
    # バッチファイル処理
    file_paths = [
        "/path/to/file1.txt",
        "/path/to/file2.csv",
        "/path/to/file3.json",
        "/path/to/file4.xml"
    ]
    result2 = data_processing.batch_process_files.delay(file_paths)
    print(f"バッチファイル処理タスク: {result2.id}")
    
    # データ集計
    result3 = data_processing.aggregate_data.delay(sample_data, "city")
    print(f"データ集計タスク: {result3.id}")
    
    return [result1, result2, result3]


def wait_for_results(results, timeout=30):
    """結果を待機して表示"""
    print(f"\n=== タスク結果 (最大{timeout}秒待機) ===")
    
    for i, result in enumerate(results, 1):
        try:
            print(f"\nタスク {i} (ID: {result.id}):")
            task_result = result.get(timeout=timeout)
            print("  状態: 成功")
            print(f"  結果: {task_result.get('message', 'メッセージなし')}")
            
            if 'result' in task_result:
                print(f"  詳細: {task_result['result']}")
                
        except Exception as e:
            print("  状態: エラーまたはタイムアウト")
            print(f"  詳細: {str(e)}")


def main():
    """メイン実行関数"""
    print("Celeryタスクテストを開始します...")
    
    all_results = []
    
    # 各種タスクをテスト
    all_results.extend(test_general_tasks())
    all_results.extend(test_ai_tasks())
    all_results.extend(test_data_tasks())
    
    print(f"\n合計 {len(all_results)} 個のタスクをキューに追加しました。")
    print("Workerで処理されるのを待機中...")
    
    # 結果を待機
    wait_for_results(all_results)
    
    print("\nテスト完了！")
    print("詳細な監視はFlower UI (http://localhost:5555) で確認できます。")


if __name__ == "__main__":
    main()
