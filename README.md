# Reversi Game

オセロゲームのWebアプリケーション

## ドキュメント

- [ER図](docs/er-diagram.drawio) - データベース設計
- [ドメインモデル図](docs/domain-model.drawio) - ドメイン駆動設計のモデル図

## 技術スタック

### バックエンド
- **言語**: Python 3.13
- **フレームワーク**: FastAPI
- **データベース**: PostgreSQL 16
- **DB接続**: psycopg3 (非同期)
- **マイグレーション**: yoyo-migrations
- **テスト**: pytest, pytest-asyncio
- **アーキテクチャ**: DDD（ドメイン駆動設計）+ クリーンアーキテクチャ

## 機能

### ゲーム機能
- 新規ゲーム作成
- 石の配置（自動裏返し処理）
- 有効手の表示
- ターンパス（有効手がない場合）
- ゲーム終了判定
- スコア計算
- ゲーム結果の保存

## 環境構築

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd reversi-game
```

### 2. 環境変数の設定

```bash
cd backend
cp .env.example .env
```

`.env`ファイルの内容：
```env
POSTGRES_URL=postgresql://user:password@db:5432/reversi
```

### 3. Docker Composeで起動

```bash
# プロジェクトルートに戻る
cd ..

# 全サービスを起動
docker compose up -d

# ログ確認
docker compose logs -f backend
```

### 4. アクセス確認

起動後、以下のURLにアクセスできます：

- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント (Swagger)**: http://localhost:8000/docs
- **Adminer (DB管理)**: http://localhost:8080
  - システム: `PostgreSQL`
  - サーバ: `db`
  - ユーザ名: `user`
  - パスワード: `password`
  - データベース: `reversi`

## プロジェクト構造

```
reversi-game/
├── backend/
│   ├── src/
│   │   ├── domain/              # ドメイン層（ビジネスロジック）
│   │   │   ├── model/           # Game, Board, Position など
│   │   │   ├── exception/       # ドメイン例外
│   │   │   └── repository/      # リポジトリインターフェース
│   │   ├── application/         # アプリケーション層
│   │   │   ├── usecase/         # StartGame, PlaceDisc など
│   │   │   ├── dto/             # データ転送オブジェクト
│   │   │   └── exception/       # アプリケーション例外
│   │   ├── infrastructure/      # インフラ層
│   │   │   ├── database/        # DB接続・マイグレーション
│   │   │   ├── repository/      # リポジトリ実装
│   │   │   └── exception/       # インフラ例外
│   │   ├── presentation/        # プレゼンテーション層
│   │   │   ├── controller/      # コントローラー
│   │   │   ├── game_router.py   # FastAPIルーター
│   │   │   └── schemas.py       # Pydanticスキーマ
│   │   └── main.py              # エントリーポイント
│   ├── tests/                   # テスト
│   ├── migrations/              # DBマイグレーション
│   └── pyproject.toml           # 依存関係定義
├── docs/                        # ドキュメント
│   ├── er-diagram.drawio        # ER図
│   └── domain-model.drawio      # ドメインモデル図
├── compose.yml                  # Docker Compose設定
└── README.md
```

### 主要ディレクトリの説明

- **domain/**: ビジネスロジックの中核。
- **application/**: ユースケースを定義。
- **infrastructure/**: DB接続など外部システムとの接続
- **presentation/**: HTTP APIエンドポイントの定義
- **tests/**: 各層の単体テスト
- **migrations/**: PostgreSQLのスキーマ定義
