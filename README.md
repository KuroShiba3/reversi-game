# Reversi Game

リバーシ（オセロ）ゲームのWebアプリケーション

## 技術スタック

### バックエンド
- **言語**: Python 3.13
- **フレームワーク**: FastAPI
- **データベース**: PostgreSQL 16
- **ORM**: なし（psycopg3で直接接続）
- **マイグレーション**: yoyo-migrations
- **アーキテクチャ**: DDD（ドメイン駆動設計）

### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: React
- **ビルドツール**: Vite

### インフラ
- **コンテナ**: Docker / Docker Compose
- **DB管理**: pgAdmin 4

## セットアップ

### 前提条件
- Docker & Docker Compose
- (オプション) Python 3.13+ (ローカル開発用)

### 起動方法

```bash
# リポジトリをクローン
git clone <repository-url>
cd reversi-game

# Docker Composeで全サービス起動
docker compose up -d

# ログ確認
docker compose logs -f backend
```

### アクセスURL

- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント (Swagger)**: http://localhost:8000/docs
- **フロントエンド**: http://localhost:5173
- **pgAdmin**: http://localhost:5050
  - Email: `admin@reversi.local`
  - Password: `admin`

### pgAdminでDBに接続

1. http://localhost:5050 にアクセス
2. 左側の「Servers」を右クリック → Create → Server
3. 以下の情報を入力:
   - **General タブ**
     - Name: `Reversi DB`
   - **Connection タブ**
     - Host: `reversi-postgres` (または `db`)
     - Port: `5432`
     - Database: `reversi`
     - Username: `user`
     - Password: `password`

## API エンドポイント

### ゲーム管理

#### 新規ゲーム開始
```bash
POST /api/games
```

**レスポンス:**
```json
{
  "game_id": "uuid",
  "board_state": [...],
  "current_player": "BLACK",
  "status": "playing"
}
```

#### ゲーム状態取得（デバッグ用）
```bash
GET /api/games/{game_id}
```

**レスポンス:**
```json
{
  "board_state": [...],
  "current_player": "BLACK",
  "black_score": 2,
  "white_score": 2,
  "status": "playing",
  "valid_moves": [
    {"row": 2, "col": 3},
    {"row": 3, "col": 2}
  ]
}
```

#### 有効手取得
```bash
GET /api/games/{game_id}/moves
```

**レスポンス:**
```json
{
  "valid_moves": [
    {"row": 2, "col": 3},
    {"row": 3, "col": 2}
  ]
}
```

#### 石を置く
```bash
POST /api/games/{game_id}/moves
Content-Type: application/json

{
  "row": 2,
  "col": 3
}
```

**レスポンス:** 204 No Content

#### ターンパス
```bash
POST /api/games/{game_id}/pass
```

**レスポンス:** 204 No Content

## 開発

### ローカル開発（Docker不使用）

```bash
# バックエンド
cd backend

# 依存関係インストール
pip install -e .

# PostgreSQLを起動（Dockerで個別起動）
docker run -d \
  --name reversi-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=reversi \
  -p 5432:5432 \
  postgres:16-alpine

# .envを編集（localhostに変更）
# POSTGRES_URL=postgresql://user:password@localhost:5432/reversi

# サーバー起動
python -m src.main
```

### マイグレーション

マイグレーションはアプリ起動時に自動実行されます。

手動で実行する場合:
```bash
cd backend
yoyo apply --database $POSTGRES_URL migrations
```

### テスト

```bash
# バックエンド
cd backend
pytest

# フロントエンド
cd frontend
npm test
```

## プロジェクト構造

```
reversi-game/
├── backend/
│   ├── src/
│   │   ├── domain/          # ドメインモデル
│   │   │   ├── model/       # エンティティ・値オブジェクト
│   │   │   └── repository/  # リポジトリインターフェース
│   │   ├── application/     # アプリケーション層
│   │   │   ├── usecase/     # ユースケース
│   │   │   └── dto/         # データ転送オブジェクト
│   │   ├── infrastructure/  # インフラ層
│   │   │   ├── database/    # DB接続・マイグレーション
│   │   │   └── repository/  # リポジトリ実装
│   │   ├── presentation/    # プレゼンテーション層
│   │   │   ├── game_router.py
│   │   │   └── schemas.py
│   │   └── main.py          # エントリーポイント
│   ├── migrations/          # DBマイグレーション
│   └── pyproject.toml
├── frontend/
│   └── src/
├── compose.yml
└── README.md
```

## ゲームルール

- 8×8の盤面
- 黒が先攻
- 相手の石を挟んで裏返す
- 置ける場所がない場合はパス
- 両者とも置けなくなったらゲーム終了
- 石の数が多い方が勝ち

## トラブルシューティング

### ポートが既に使用されている
```bash
# 使用中のポートを確認
lsof -i :8000
lsof -i :5432

# Dockerコンテナを停止
docker compose down
```

### マイグレーションエラー
```bash
# データベースをリセット
docker compose down -v
docker compose up -d
```

### pgAdminに接続できない
- Dockerネットワーク内では `db` または `reversi-postgres` をホスト名として使用
- ローカルから接続する場合は `localhost:5432`

## ライセンス

MIT
