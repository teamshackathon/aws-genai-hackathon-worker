"""
Celeryタスクをテストするためのクライアントスクリプト
"""

from tasks import general


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


def wait_for_results(results, timeout=30):
    """結果を待機して表示"""
    print(f"\n=== タスク結果 (最大{timeout}秒待機) ===")

    for i, result in enumerate(results, 1):
        try:
            print(f"\nタスク {i} (ID: {result.id}):")
            task_result = result.get(timeout=timeout)
            print("  状態: 成功")
            print(f"  結果: {task_result.get('message', 'メッセージなし')}")

            if "result" in task_result:
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

    print(f"\n合計 {len(all_results)} 個のタスクをキューに追加しました。")
    print("Workerで処理されるのを待機中...")

    # 結果を待機
    wait_for_results(all_results)

    print("\nテスト完了！")
    print("詳細な監視はFlower UI (http://localhost:5555) で確認できます。")


if __name__ == "__main__":
    main()
