# AWS GenAI Hackathon Worker

このプロジェクトは、CeleryとRedisを使用した非同期タスク処理ワーカーです。

## 機能

- **基本タスク処理**: 数値計算、テキスト処理
- **AI処理**: 感情分析、テキスト要約
- **データ処理**: CSVデータ処理、バッチ処理、データ集計
- **Redis Queue処理**: レシピ生成タスクの非同期処理
- **優先度キュー**: high_priority, normal, low_priority
- **監視**: Flower UI でタスクの監視が可能

## 前提条件

- Docker & Docker Compose
- Redis (localhost:6379で稼働中)

## セットアップ

### 1. 環境設定

```bash
cp .env.example .env
```

### 2. Dockerでワーカーを起動

```bash
docker compose up -d
```

これにより以下のサービスが起動します：
- `worker`: Celeryワーカー
- `flower`: 監視UI (http://localhost:5555)
- `beat`: 定期実行スケジューラー

## 使用方法

### タスクの実行

```bash
python main.py
```

### 特定のタスクを実行

```python
from tasks.general import add_numbers
from tasks.ai_processing import analyze_sentiment
from tasks.data_processing import process_csv_data

# 数値計算
result = add_numbers.delay(10, 20)
print(f"Task ID: {result.id}")

# 感情分析
sentiment_result = analyze_sentiment.delay("I love this project!")
print(f"Sentiment Task ID: {sentiment_result.id}")

# データ処理
data = [{"name": "Alice", "age": "25"}]
data_result = process_csv_data.delay(data)
print(f"Data Task ID: {data_result.id}")
```

### Redis Queueを使用したレシピ生成タスク

```bash
# テスト用のレシピ生成タスクをキューに追加
python test_queue.py

# Redis queueワーカーを開始（キューからタスクを取得・処理）
python queue_worker.py
```

```python
# プログラムからレシピ生成タスクを利用
from tasks.queue_processor import QueueProcessor

processor = QueueProcessor()

# タスクをキューに追加（例：別のアプリケーションから）
task_data = {
    "task_id": "recipe_gen_test_123",
    "session_id": "session_456",
    "url": "https://example.com/recipe",
    "user_id": 789,
    "priority": 1,
    "created_at": "2025-06-15T10:00:00Z",
    "status": "queued"
}

# タスクステータスの確認
status = processor.get_task_status("recipe_gen_test_123")
print(f"Task Status: {status}")
```

### タスク結果の確認

```bash
# 特定のタスクの結果を確認
python check_result.py <task_id>

# アクティブなタスクの一覧
python check_result.py --list
```

## 監視

Flower UI でタスクの状況を監視できます：
- URL: http://localhost:5555
- リアルタイムでタスクの実行状況を確認
- ワーカーの状態を監視
- タスクの履歴を確認

## Celeryコマンド

### ワーカーを直接起動

```bash
celery -A celery_app worker --loglevel=info
```

### 特定のキューのみ処理

```bash
celery -A celery_app worker --loglevel=info --queues=ai_queue
```

### Flowerを起動

```bash
celery -A celery_app flower
```

## プロジェクト構造

```
├── celery_app.py          # Celeryアプリケーション設定
├── config.py              # 設定管理 (Pydantic)
├── main.py                # メイン実行ファイル
├── check_result.py        # タスク結果確認スクリプト
├── docker-compose.yml     # Docker構成
├── Dockerfile            # Dockerイメージ設定
├── requirements.prod.txt  # 本番依存関係
├── requirements.dev.txt   # 開発依存関係
└── tasks/                # タスク定義
    ├── general.py         # 基本タスク
    ├── ai_processing.py   # AI処理タスク
    └── data_processing.py # データ処理タスク
```

## 開発

### 依存関係のインストール

```bash
pip install -r requirements.dev.txt
```

### コードフォーマット

```bash
ruff check ./ --fix
black .
```

### テスト実行

```bash
pytest
```

## トラブルシューティング

### Redisに接続できない場合

1. Redisが起動しているか確認
2. `config.py`の接続設定を確認
3. Dockerの場合、`host.docker.internal`を使用

### タスクが実行されない場合

1. ワーカーが起動しているか確認
2. キューの設定を確認
3. Flowerで状況を確認
