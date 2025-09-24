# Docker デプロイ戦略 (修正版)

## 🐳 公式uvDockerイメージ活用

### uvの公式Dockerイメージ発見
調査の結果、uvには**公式Dockerイメージ**が存在することが判明：
- イメージ: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- プロベナンス検証: GitHub Actionsで自動ビルド・署名
- 公式サポート: astral-sh組織による保守

## 📋 最終Dockerファイル仕様

### バックエンド (backend.Dockerfile)
```dockerfile
# uvの公式Dockerイメージを使用
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock ./

# 本番用依存関係をインストール
# --frozen: uv.lockファイルを厳密に使用（再解決しない）
# --no-dev: 開発用依存関係を除外
RUN uv sync --frozen --no-dev

# ソースコードとプロンプトをコピー
COPY src/ ./src/
COPY prompts/ ./prompts/

# 環境変数設定
ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

# アプリケーション起動 (make dev-apiと同等)
CMD ["uv", "run", "uvicorn", "src.hibikasu_agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### フロントエンド (frontend.Dockerfile)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# pnpmをインストール
RUN npm install -g pnpm

# パッケージファイルをコピー
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# 依存関係をインストール
RUN pnpm install --frozen-lockfile

# ソースコードをコピー
COPY frontend/ .

# 本番用ビルド
RUN pnpm build

EXPOSE 3000

# 本番サーバー起動
CMD ["pnpm", "start"]
```

## 🔧 必要な環境変数

### バックエンド環境変数
```bash
# 必須
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id

# AI設定
HIBIKASU_API_MODE=ai
ADK_MODEL=gemini-2.5-flash-lite
ADK_REVIEW_TIMEOUT_SEC=40

# その他
GOOGLE_GENAI_USE_VERTEXAI=FALSE
LOG_LEVEL=INFO
HIBIKASU_LOG_LEVEL=INFO
CORS_ALLOW_ORIGINS=https://your-frontend-url.a.run.app
```

### フロントエンド環境変数
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.a.run.app
```

## 📦 必要な設定ファイル

### Next.js設定更新 (frontend/next.config.ts)
```typescript
const parseAllowed = (val?: string) =>
  (val || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

const allowedFromEnv = parseAllowed(process.env.ALLOWED_DEV_ORIGINS);

const nextConfig = {
  // Cloud Run用の設定
  output: 'standalone',

  // 既存の開発用設定を保持
  allowedDevOrigins: allowedFromEnv.length
    ? allowedFromEnv
    : ["http://localhost:3000", "http://127.0.0.1:3000"],

  // 本番環境用の設定
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  }
};

export default nextConfig;
```

### .dockerignore
```
# Backend用
.env
.env.local
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
node_modules/

# Frontend用
.next/
node_modules/
.env.local
```

## 🚀 ビルド・デプロイ手順

### 1. ローカルテスト
```bash
# バックエンドビルド・テスト
uv lock  # ロックファイル更新
docker build -f backend.Dockerfile -t hibikasu-backend .
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key \
  -e HIBIKASU_API_MODE=ai \
  hibikasu-backend

# フロントエンドビルド・テスト
docker build -f frontend.Dockerfile -t hibikasu-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8080 \
  hibikasu-frontend
```

### 2. Cloud Build設定 (cloudbuild.yaml)
```yaml
steps:
  # バックエンドビルド
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/hibikasu-backend:$COMMIT_SHA',
      '-f', 'backend.Dockerfile',
      '.'
    ]

  # フロントエンドビルド
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/hibikasu-frontend:$COMMIT_SHA',
      '-f', 'frontend.Dockerfile',
      '.'
    ]

  # バックエンドデプロイ
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args: [
      'run', 'deploy', 'hibikasu-backend',
      '--image', 'gcr.io/$PROJECT_ID/hibikasu-backend:$COMMIT_SHA',
      '--region', 'asia-northeast1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--set-env-vars', 'GOOGLE_CLOUD_PROJECT=$PROJECT_ID,HIBIKASU_API_MODE=ai,ADK_MODEL=gemini-2.5-flash-lite',
      '--set-secrets', 'GOOGLE_API_KEY=gemini-api-key:latest'
    ]

  # フロントエンドデプロイ
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args: [
      'run', 'deploy', 'hibikasu-frontend',
      '--image', 'gcr.io/$PROJECT_ID/hibikasu-frontend:$COMMIT_SHA',
      '--region', 'asia-northeast1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--set-env-vars', 'NEXT_PUBLIC_API_BASE_URL=https://hibikasu-backend-xxx.a.run.app'
    ]

images:
  - 'gcr.io/$PROJECT_ID/hibikasu-backend:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/hibikasu-frontend:$COMMIT_SHA'
```

## ✅ 検証ポイント

### 1. 必要なファイル存在確認
- [ ] `pyproject.toml`, `uv.lock`
- [ ] `prompts/agents.toml` (9種類エージェント定義)
- [ ] `src/hibikasu_agent/api/main.py`
- [ ] `frontend/package.json`, `frontend/pnpm-lock.yaml`

### 2. 起動コマンド一致確認
- [x] バックエンド: `uv run uvicorn src.hibikasu_agent.api.main:app`
- [x] フロントエンド: `pnpm dev` → `pnpm start`

### 3. 環境変数対応確認
- [x] .env.exampleの内容をCloud Run環境変数に対応
- [x] Secret Manager統合 (GOOGLE_API_KEY)

## 🔍 差分・改善点

### 公式uvイメージ使用の利点
1. **信頼性**: GitHub Actionsで自動ビルド・署名
2. **最適化**: Python環境が事前設定済み
3. **セキュリティ**: 定期的なセキュリティ更新
4. **効率性**: uvのインストール処理不要

### 対応完了事項
- ✅ uvの公式インストール方法確認
- ✅ `uv sync --frozen --no-dev`の正当性確認
- ✅ プロンプトファイルの必要性確認
- ✅ Next.js本番ビルド手順確認
- ✅ 環境変数の洗い出し完了

この修正版で実装を進めて問題ないでしょうか？
