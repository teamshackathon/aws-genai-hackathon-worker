import logging
import time
from typing import Any, Dict, List

from celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def process_csv_data(self, data: List[Dict[str, Any]]) -> dict:
    """CSV形式のデータを処理するタスク"""
    try:
        logger.info(f"タスク {self.request.id}: CSVデータ処理開始 - {len(data)}行")
        
        total_rows = len(data)
        processed_data = []
        
        for i, row in enumerate(data):
            # 進捗状況を更新
            if i % 10 == 0:  # 10行ごとに進捗更新
                progress = int((i / total_rows) * 100)
                self.update_state(
                    state="PROGRESS", 
                    meta={"current": progress, "total": 100, "processed_rows": i, "total_rows": total_rows}
                )
            
            # データ処理のシミュレーション
            processed_row = {}
            for key, value in row.items():
                if isinstance(value, str) and value.isdigit():
                    processed_row[key] = int(value)
                elif isinstance(value, str):
                    processed_row[key] = value.strip().title()
                else:
                    processed_row[key] = value
            
            processed_data.append(processed_row)
            time.sleep(0.01)  # 処理時間をシミュレート
        
        # 統計情報を計算
        stats = {
            "total_rows": total_rows,
            "columns": list(data[0].keys()) if data else [],
            "processing_time": total_rows * 0.01
        }
        
        logger.info(f"タスク {self.request.id}: CSVデータ処理完了")
        
        return {
            "status": "SUCCESS",
            "processed_data": processed_data,
            "statistics": stats,
            "message": f"{total_rows}行のデータ処理が完了しました"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def batch_process_files(self, file_paths: List[str]) -> dict:
    """複数ファイルのバッチ処理タスク"""
    try:
        logger.info(f"タスク {self.request.id}: バッチ処理開始 - {len(file_paths)}ファイル")
        
        results = []
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            # 進捗状況を更新
            progress = int((i / total_files) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "current_file": file_path,
                    "processed_files": i,
                    "total_files": total_files
                }
            )
            
            # ファイル処理のシミュレーション
            file_result = {
                "file_path": file_path,
                "status": "processed",
                "size": len(file_path) * 100,  # ダミーサイズ
                "processed_at": time.time()
            }
            
            results.append(file_result)
            time.sleep(1)  # 処理時間をシミュレート
        
        logger.info(f"タスク {self.request.id}: バッチ処理完了")
        
        return {
            "status": "SUCCESS",
            "processed_files": results,
            "total_processed": len(results),
            "total_size": sum(r["size"] for r in results),
            "message": f"{len(results)}ファイルのバッチ処理が完了しました"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def aggregate_data(self, data_points: List[Dict[str, Any]], group_by: str) -> dict:
    """データ集計タスク"""
    try:
        logger.info(f"タスク {self.request.id}: データ集計開始 - {len(data_points)}データポイント")
        
        self.update_state(state="PROGRESS", meta={"current": 25, "total": 100, "step": "データ準備中..."})
        time.sleep(1)
        
        # グループ化
        groups = {}
        for point in data_points:
            key = point.get(group_by, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(point)
        
        self.update_state(state="PROGRESS", meta={"current": 50, "total": 100, "step": "集計処理中..."})
        time.sleep(2)
        
        # 集計
        aggregated = {}
        for group_key, group_data in groups.items():
            aggregated[group_key] = {
                "count": len(group_data),
                "items": group_data
            }
        
        self.update_state(state="PROGRESS", meta={"current": 80, "total": 100, "step": "結果整理中..."})
        time.sleep(1)
        
        logger.info(f"タスク {self.request.id}: データ集計完了 - {len(groups)}グループ")
        
        return {
            "status": "SUCCESS",
            "aggregated_data": aggregated,
            "total_groups": len(groups),
            "total_items": len(data_points),
            "group_by": group_by,
            "message": f"{group_by}による集計が完了しました（{len(groups)}グループ）"
        }
    
    except Exception as exc:
        logger.error(f"タスク {self.request.id}: エラー発生 - {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
