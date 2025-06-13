"""
Celeryタスクの結果を確認するスクリプト
"""
import sys
import json
from celery.result import AsyncResult
from celery_app import app


def check_task_result(task_id: str):
    """タスクの結果を確認"""
    result = AsyncResult(task_id, app=app)
    
    print(f"タスクID: {task_id}")
    print(f"状態: {result.state}")
    
    if result.state == 'PENDING':
        print("タスクは待機中または存在しません")
    elif result.state == 'PROGRESS':
        print(f"進捗: {result.info}")
    elif result.state == 'SUCCESS':
        print("タスクが正常に完了しました")
        print(f"結果: {json.dumps(result.result, indent=2, ensure_ascii=False)}")
    elif result.state == 'FAILURE':
        print("タスクが失敗しました")
        print(f"エラー: {result.info}")
    else:
        print(f"不明な状態: {result.state}")
        print(f"情報: {result.info}")


def list_active_tasks():
    """アクティブなタスクを一覧表示"""
    inspect = app.control.inspect()
    
    # アクティブなタスク
    active_tasks = inspect.active()
    if active_tasks:
        print("=== アクティブなタスク ===")
        for worker, tasks in active_tasks.items():
            print(f"Worker: {worker}")
            for task in tasks:
                print(f"  - {task['id']}: {task['name']}")
    else:
        print("アクティブなタスクはありません")
    
    # 予約されたタスク
    reserved_tasks = inspect.reserved()
    if reserved_tasks:
        print("\n=== 予約されたタスク ===")
        for worker, tasks in reserved_tasks.items():
            print(f"Worker: {worker}")
            for task in tasks:
                print(f"  - {task['id']}: {task['name']}")


def main():
    if len(sys.argv) < 2:
        print("使用法:")
        print("  python check_result.py <task_id>  # 特定のタスクの結果を確認")
        print("  python check_result.py --list     # アクティブなタスクを一覧表示")
        return
    
    if sys.argv[1] == '--list':
        list_active_tasks()
    else:
        task_id = sys.argv[1]
        check_task_result(task_id)


if __name__ == "__main__":
    main()
