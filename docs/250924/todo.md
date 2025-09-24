## 2025-09-24 タスク整理（Cloud Run デプロイ & 名称移行）

### 0. 前提共有
- MVPデプロイは既存名称 `Hibikasu` で進行、安定後に公式名称 `Revural` へリネーム。
- バックエンド: FastAPI (`src/hibikasu_agent/api/main.py`)、uv + Google ADK 依存。
- フロントエンド: Next.js 15 (+pnpm)。

### 1. バックエンド Cloud Run 準備
- [x] `backend.Dockerfile` 作成（ベース: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`）。
  - [x] `pyproject.toml` / `uv.lock` コピー → `uv sync --frozen --no-dev`。
  - [x] `src/` と `prompts/` のCOPY、`ENV PORT=8080` 設定。
  - [x] `CMD ["uv", "run", "uvicorn", "src.hibikasu_agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]`。
- [x] ランタイムENV定義整理。
  - [x] `GOOGLE_API_KEY` を Secret Manager から供給。
  - [x] `HIBIKASU_API_MODE=ai`, `ADK_MODEL=gemini-2.5-flash-lite`。
  - [x] `CORS_ALLOW_ORIGINS=https://hibikasu-frontend-<hash>.a.run.app`（デプロイ後に更新済み: https://hibikasu-frontend-ev4pox6gua-an.a.run.app）
  - [x] `HIBIKASU_LOG_LEVEL`, `LOG_LEVEL` のデフォルト確認。
- [x] `cloudbuild.yaml` にバックエンドビルド/デプロイステップ追加。
- [x] Cloud Run サービス `hibikasu-backend` 作成（asia-northeast1）。 # revision hibikasu-backend-00004-qsk / URL: https://hibikasu-backend-ev4pox6gua-an.a.run.app
  - [x] `--allow-unauthenticated`, `--timeout 300`, `--memory 1Gi` など設定チューニング。
  - [x] Secret Manager バインド (`GOOGLE_API_KEY`)。
- [x] ローカルテスト: `docker build`, `docker run -p 8080:8080 ...`。 # Docker build & mock API smoke test（port 18080）完了
- [x] **初回デプロイは「バックエンド → フロントエンド → CORS再設定」の順で実施し、発行URLを基に環境変数を更新する。**

### 2. フロントエンド Cloud Run 準備
- [x] `frontend.Dockerfile` 作成（ベース: `node:20-bookworm-slim`）。
  - [x] `corepack enable && pnpm install --frozen-lockfile`。
  - [x] `pnpm build` 後、`pnpm start -- -H 0.0.0.0 -p ${PORT:-8080}`。 # Dockerfileで起動コマンド整備済み
  - [x] `ENV NODE_ENV=production`, `ENV PORT=8080`。
- [x] `frontend/next.config.ts` 更新。
  - [x] `output: 'standalone'` 追加。
  - [x] 環境変数透過: `env: { NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000" }`。
  - [ ] 不要になった `allowedDevOrigins` が本番に影響しないこと確認。（現状カスタムプロパティとして残置。利用箇所未確認のため継続ウォッチ）
- [x] Cloud Run サービス `hibikasu-frontend` 作成。 # revision hibikasu-frontend-00002-vnc / URL: https://hibikasu-frontend-ev4pox6gua-an.a.run.app
  - [x] `NEXT_PUBLIC_API_BASE_URL` をバックエンドURLに設定。 # https://hibikasu-backend-ev4pox6gua-an.a.run.app
  - [x] 必要なら `--set-env-vars NODE_ENV=production`。
- [x] ローカルテスト: `docker build --platform=linux/amd64`, `docker run -p 13000:8080 ...`。 # frontendコンテナ起動→Next応答200確認

### 3. 共通設定・CI/CD
- [x] Dockerfile 作業と同時に `.dockerignore` を整備（Python/Node両方の不要ファイル、`.venv`, `.next`, `node_modules` 等を除外）。
- [x] `cloudbuild.yaml` 全体設計。
  - [x] Cloud Build でのテスト実行（build 542c8dba-b311-469b-a797-18edec02859b 成功）。
  - [x] バックエンド → フロントエンドの順でビルド。
  - [x] `images:` セクション更新。
  - [x] デプロイ時のENV/Secret指定を `args` に追記。
- [x] Cloud Build SA に権限付与。
  - [x] `roles/run.admin`, `roles/iam.serviceAccountUser`, `roles/storage.admin`, `roles/secretmanager.secretAccessor`。
- [ ] Cloud Build トリガー作成（mainブランチ push など）。
- [ ] ログ監視: Cloud Logging のクエリテンプレ準備。

### 4. 動作確認チェックリスト
- [ ] フロント→バック通信で CORS エラーが出ない。
- [ ] `/reviews` POST/GET 正常応答（Mockモード/AIモード両方）。
- [ ] Cloud Run Logs でFastAPIのINFOログ確認。
- [ ] エラーハンドリング: Gemini API失敗時のレスポンス確認。
- [ ] 利用料金試算をREADME or docsへ記載。

### 5. ドキュメント整備
- [ ] README に Cloud Run デプロイ手順追記。
- [ ] `docs/250923/google_cloud_hackathon_deployment_guide.md` を最新版に更新（コンテナ手順差し替え）。
- [ ] 新しい `cloudbuild.yaml` / Dockerfile に対する知見を docs 化。
- [ ] チーム向け Runbook (トラブルシューティング) 作成。

### 6. Revural への名称移行（デプロイ安定後に実施）
- [ ] リポジトリのルートパッケージ `src/hibikasu_agent` → `src/revural_agent` へのリネーム計画作成。
  - [ ] `pyproject.toml` / import パスの一括置換手順整理。
  - [ ] `HIBIKASU_*` 環境変数 → `REVURAL_*` に置換。
- [ ] Cloud Run サービス名の焼き直し（新URL発行）または独自ドメイン導入。
- [ ] Secret Manager などGCPリソース名の整理。
- [ ] Zenn記事/README/Docs のブランド名更新。
- [ ] ロールアウト戦略: 旧名称→新名称への切り替え通知、APIクライアント影響確認。

### 7. 未決定事項
- [ ] Cloud Run→Load Balancer 統合の要否（本番ドメイン統一タイミング）。
- [ ] Gemini API コスト・Quota増加時のスケール戦略。
- [ ] ローカル開発用 Mock/AI モード切り替えUIの要不要。

> 必要に応じて、タスクを Issue / PR ベースに分割して運用すること。まずは 1 と 2 を最優先で片付ける。

### 8. Cloud Run 実デプロイ手順（要GCP権限）
- [ ] gcloud 認証とプロジェクト設定
  - [ ] `gcloud auth login`
  - [ ] `gcloud config set project <PROJECT_ID>`（例: `zerebom-private`）
  - [x] 必要なAPIを有効化: `gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com containerregistry.googleapis.com`
- [x] Secret Manager 準備
  - [x] Gemini APIキーを登録: `echo 'YOUR_GEMINI_API_KEY' | gcloud secrets create gemini-api-key --data-file=-`
  - [x] Cloud BuildサービスアカウントにSecret閲覧権限: `gcloud secrets add-iam-policy-binding gemini-api-key --member="serviceAccount:531211843908@cloudbuild.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"`
  - [x] Cloud Run 実行サービスアカウントにもSecret閲覧権限を付与（初期デプロイ前のためデフォルトSA `$(PROJECT_NUMBER)-compute@developer.gserviceaccount.com` に付与済み。サービス作成後に専用SAへ切替予定）
- [x] Cloud Build サービスアカウント権限付与
  - [x] `roles/run.admin`
  - [x] `roles/iam.serviceAccountUser`
  - [x] `roles/storage.admin`
- [x] Cloud Build 実行
  - [x] `gcloud builds submit --config=cloudbuild.yaml --substitutions=...` # build 542c8dba-b311-469b-a797-18edec02859b
- [x] Cloud Run URL 取得と環境変数更新
  - [x] `BACKEND_URL=$(gcloud run services describe hibikasu-backend --region=asia-northeast1 --format='value(status.url)')`
  - [x] `FRONTEND_URL=$(gcloud run services describe hibikasu-frontend --region=asia-northeast1 --format='value(status.url)')`
  - [x] フロントエンドにバックエンドURLを反映: `gcloud run services update hibikasu-frontend --region=asia-northeast1 --set-env-vars=NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL`
  - [x] バックエンドCORSをフロントURLに更新: `gcloud run services update hibikasu-backend --region=asia-northeast1 --set-env-vars=CORS_ALLOW_ORIGINS=$FRONTEND_URL`
- [x] 動作確認
  - [x] `curl -s -X POST "$BACKEND_URL/reviews" -H 'Content-Type: application/json' -d '{"prd_text":"Cloud Run疎通テスト"}'`
  - [ ] ブラウザで `FRONTEND_URL` にアクセスし、レビュー実行がバックエンドと連携するか確認
