# Google Cloud ハッカソン デプロイガイド

## 📋 要件確認

### Google Cloud ハッカソン必須条件

#### ✅ Google Cloud AI技術の利用 (既に適合)
- **ADK (Agent Development Kit)**: ✅ 実装済み
- **Gemini API**: ✅ gemini-2.5-flash-lite使用中
- **マルチエージェントシステム**: ✅ 9種類の専門AIエージェント

#### ❌ Google Cloud アプリケーション実行プロダクトの利用 (要実装)
以下のいずれかを使用する必要があります：
- App Engine
- Google Compute Engine
- Google Kubernetes Engine (GKE)
- **Cloud Run** ← 推奨
- Cloud Functions
- Cloud TPU / GPU

## 🏗️ 現在のアーキテクチャ

### アプリケーション構成
```
├── バックエンド: FastAPI (Python 3.12+)
│   ├── AI エージェント: 9種類専門家AI
│   ├── API: レビュー管理、エージェント選択
│   └── ポート: 8000
├── フロントエンド: Next.js 15.5.2
│   ├── UI: エージェント選択、結果表示
│   └── ポート: 3000
└── AI統合: Google ADK + Gemini API
```

### 専門AIエージェント (9種類)
1. **エンジニアAI** - バックエンド設計・API専門
2. **UXデザイナーAI** - ユーザー体験設計専門
3. **QAテスターAI** - 品質保証・テスト戦略専門
4. **プロダクトマネージャーAI** - ビジネス価値・戦略専門
5. **データサイエンティストAI** - 効果測定・分析専門
6. **UXライターAI** - マイクロコピー・ブランドボイス専門
7. **セキュリティAI** - 脆弱性診断・個人情報保護専門
8. **マーケティングAI** - GTM戦略・競合分析専門
9. **リーガルAI** - 法務・コンプライアンス専門

## 🚀 デプロイ計画

### 推奨アーキテクチャ: Cloud Run
```
Internet → Cloud Load Balancer → Cloud Run Services
                                  ├── Frontend Service (Next.js)
                                  └── Backend Service (FastAPI)
                                       └── Gemini API
```

### 利点
- サーバーレス（従量課金）
- 自動スケーリング
- 無料枠: 月200万リクエスト
- HTTPS自動提供

## 📦 必要なファイル

### 1. バックエンド Dockerfile
```dockerfile
# backend.Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8080

# Start the application
CMD ["uv", "run", "uvicorn", "src.hibikasu_agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. フロントエンド Dockerfile
```dockerfile
# frontend.Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile --production

# Copy source code
COPY frontend/ .

# Build the application
RUN pnpm build

# Expose port
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
```

### 3. Next.js設定更新
```javascript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  },
  // Cloud Run用の最適化
  experimental: {
    outputFileTracingRoot: process.cwd(),
  }
}

module.exports = nextConfig
```

### 4. Cloud Build設定
```yaml
# cloudbuild.yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/hibikasu-backend:$COMMIT_SHA',
      '-f', 'backend.Dockerfile',
      '.'
    ]

  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/hibikasu-frontend:$COMMIT_SHA',
      '-f', 'frontend.Dockerfile',
      '.'
    ]

  # Deploy backend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args: [
      'run', 'deploy', 'hibikasu-backend',
      '--image', 'gcr.io/$PROJECT_ID/hibikasu-backend:$COMMIT_SHA',
      '--region', 'asia-northeast1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--set-env-vars', 'GOOGLE_CLOUD_PROJECT=$PROJECT_ID'
    ]

  # Deploy frontend to Cloud Run
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

## 🔧 環境設定

### 必要な環境変数

#### バックエンド
```bash
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id
CORS_ALLOW_ORIGINS=https://your-frontend-url.a.run.app
HIBIKASU_LOG_LEVEL=INFO
ADK_MODEL=gemini-2.5-flash-lite
```

#### フロントエンド
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.a.run.app
```

### Secret Manager使用 (推奨)
```bash
# Gemini API Keyをシークレットとして保存
gcloud secrets create gemini-api-key --data-file=-
echo "your_actual_api_key_here" | gcloud secrets create gemini-api-key --data-file=-

# Cloud Runサービスからアクセス許可
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:your-service-account@your-project.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 📋 デプロイ手順

### 1. Google Cloud プロジェクト準備
```bash
# プロジェクト作成
gcloud projects create your-hibikasu-project

# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. ローカルでのDockerテスト
```bash
# バックエンドビルド・テスト
docker build -f backend.Dockerfile -t hibikasu-backend .
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key \
  hibikasu-backend

# フロントエンドビルド・テスト
docker build -f frontend.Dockerfile -t hibikasu-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:8080 \
  hibikasu-frontend
```

### 3. Cloud Runデプロイ
```bash
# Cloud Buildでビルド・デプロイ
gcloud builds submit --config cloudbuild.yaml .

# または手動デプロイ
gcloud run deploy hibikasu-backend \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## 📊 コスト見積もり

### Cloud Run料金 (東京リージョン)
- **CPU**: $0.000024/vCPU秒
- **メモリ**: $0.0000025/GB秒
- **リクエスト**: $0.0000004/リクエスト
- **無料枠**: 200万リクエスト/月、36万vCPU秒/月

### 想定使用量 (ハッカソン期間)
- デモ・テスト: ~1000リクエスト/日
- **月額費用**: ~$5-10 (無料枠内)

## 📝 提出物準備

### 1. GitHub公開リポジトリ
- [ ] リポジトリを公開に変更
- [ ] README.md更新（デプロイ手順含む）
- [ ] デプロイ用ファイル追加

### 2. Zenn記事作成項目
#### 必須内容:
- **ユーザー像と課題**: PMやマーケター向けの高品質PRDレビューサービス
- **ソリューション**: 9種類の専門AIエージェントによるマルチアングル分析
- **システムアーキテクチャ図**: Cloud Run + Gemini API構成
- **3分デモ動画**: YouTube公開 → Zenn埋め込み

#### アーキテクチャ図例:
```
[ユーザー] → [Next.js Frontend (Cloud Run)]
                ↓ API Call
           [FastAPI Backend (Cloud Run)]
                ↓ ADK Integration
           [Gemini API (9 AI Agents)]
                ↓ Analysis Results
           [構造化された専門家レビュー]
```

### 3. デモ動画構成案
1. **問題提起** (30秒): PRDレビューの課題
2. **ソリューション紹介** (30秒): 9種類のAI専門家
3. **実際のデモ** (90秒): エージェント選択→レビュー実行→結果確認
4. **価値まとめ** (30秒): 導入効果

## ⚠️ 注意事項

### セキュリティ
- Gemini API Keyは絶対にコードに含めない
- Secret Manager使用推奨
- CORS設定を本番URL用に更新

### 性能
- Cloud Runコールドスタート対策（keep-alive設定）
- Gemini APIレート制限考慮
- フロントエンドの静的アセット最適化

### 運用
- ログ監視設定
- エラー通知設定
- デプロイ後の動作確認チェックリスト

## 🎯 実装優先度

### Phase 1: 基本デプロイ (最優先)
1. Dockerファイル作成
2. Cloud Runデプロイ
3. 基本動作確認

### Phase 2: 本格運用準備
1. Secret Manager統合
2. 監視・ログ設定
3. CORS・セキュリティ強化

### Phase 3: 提出準備
1. リポジトリ公開
2. Zenn記事執筆
3. デモ動画作成

次のステップとして、どのファイルから作成を始めますか？
