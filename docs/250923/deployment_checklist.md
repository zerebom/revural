# Google Cloud ハッカソン デプロイチェックリスト

## 📋 提出要件チェック

### 必須条件
- [ ] **Google Cloud アプリケーション実行プロダクト使用**
  - [ ] Cloud Run デプロイ完了
  - [ ] バックエンドURL取得
  - [ ] フロントエンドURL取得

- [ ] **Google Cloud AI技術使用** ✅ 実装済み
  - [x] ADK (Agent Development Kit)
- [x] Gemini API (gemini-2.5-flash-lite)

### 提出物
- [ ] **GitHub公開リポジトリURL**
  - [ ] リポジトリを公開に変更
  - [ ] README.md にデプロイ手順追加
  - [ ] Dockerファイル等のデプロイ設定ファイル追加

- [ ] **デプロイURL**
  - [ ] フロントエンドURL (動作確認済み)
  - [ ] バックエンドURL (API動作確認済み)

- [ ] **Zenn記事URL**
  - [ ] 記事作成・公開
  - [ ] カテゴリ「Idea」で投稿
  - [ ] 必須内容 ⅰ〜ⅲ 含む

## 🚀 デプロイ作業チェックリスト

### Phase 1: 基本設定
- [ ] Google Cloud プロジェクト作成
- [ ] 必要なAPI有効化
  - [ ] Cloud Run API
  - [ ] Cloud Build API
  - [ ] Container Registry API
  - [ ] Secret Manager API

### Phase 2: Dockerファイル作成
- [ ] `backend.Dockerfile` 作成
- [ ] `frontend.Dockerfile` 作成
- [ ] `next.config.js` 更新
- [ ] `cloudbuild.yaml` 作成

### Phase 3: ローカルテスト
- [ ] バックエンドDockerビルド・動作確認
- [ ] フロントエンドDockerビルド・動作確認
- [ ] 疎通テスト (frontend → backend → Gemini API)

### Phase 4: Cloud Runデプロイ
- [ ] バックエンドデプロイ
- [ ] フロントエンドデプロイ
- [ ] 環境変数設定
- [ ] CORS設定確認

### Phase 5: 動作確認
- [ ] フロントエンド画面表示確認
- [ ] エージェント選択機能確認
- [ ] PRDレビュー実行確認
- [ ] 9種類エージェントレスポンス確認

## 📝 Zenn記事必須内容

### ⅰ. プロダクト説明
- [ ] **対象ユーザー像**
  - プロダクトマネージャー
  - マーケティング担当者
  - プロダクト企画者

- [ ] **課題**
  - PRDレビューの属人性
  - 専門性不足による見落とし
  - レビュー工数の増大

- [ ] **ソリューション**
  - 9種類の専門AIエージェント
  - マルチアングル分析
  - 構造化されたフィードバック

- [ ] **特徴**
  - エージェント選択機能
  - リアルタイムレビュー
  - Google ADK活用

### ⅱ. システムアーキテクチャ図
```
[ユーザー]
    ↓
[Next.js Frontend (Cloud Run)]
    ↓ REST API
[FastAPI Backend (Cloud Run)]
    ↓ ADK Integration
[Gemini API]
    ↓ 9 AI Specialists
[構造化レビュー結果]
```

- [ ] アーキテクチャ図作成
- [ ] 技術スタック明記
- [ ] データフロー説明

### ⅲ. デモ動画 (3分)
- [ ] **導入** (30秒)
  - 課題提起
  - ソリューション概要

- [ ] **デモ** (120秒)
  - PRD入力
  - エージェント選択
  - レビュー実行
  - 結果確認
  - 複数エージェントの違い紹介

- [ ] **まとめ** (30秒)
  - 価値・効果
  - 今後の展望

- [ ] YouTube公開
- [ ] Zenn記事埋め込み

## 🔧 設定ファイル作成

### 必要ファイル
- [ ] `backend.Dockerfile`
- [ ] `frontend.Dockerfile`
- [ ] `next.config.js` 更新
- [ ] `cloudbuild.yaml`
- [ ] `.dockerignore`
- [ ] 環境変数設定

### 環境変数
#### バックエンド
- [ ] `GOOGLE_API_KEY`
- [ ] `GOOGLE_CLOUD_PROJECT`
- [ ] `CORS_ALLOW_ORIGINS`
- [ ] `HIBIKASU_LOG_LEVEL`

#### フロントエンド
- [ ] `NEXT_PUBLIC_API_BASE_URL`

## ⚠️ 注意事項

### セキュリティ
- [ ] API Keyをコードに含めない
- [ ] Secret Manager使用
- [ ] 適切なCORS設定

### 動作確認
- [ ] 全エージェント動作確認
- [ ] エラーハンドリング確認
- [ ] レスポンシブ対応確認

### コスト
- [ ] 無料枠内での利用確認
- [ ] 想定利用量の見積もり

## 📊 進捗管理

### 完了済み ✅
- [x] 9種類エージェント実装
- [x] エージェント選択UI実装
- [x] Google ADK統合
- [x] Gemini API連携

### 実装中 🚧
- [ ] Dockerファイル作成
- [ ] Cloud Runデプロイ設定

### 未着手 ⏳
- [ ] リポジトリ公開
- [ ] Zenn記事執筆
- [ ] デモ動画作成

## 🎯 次のアクション

1. **最優先**: Dockerファイル作成
2. Cloud Runデプロイ
3. 動作確認
4. リポジトリ公開
5. Zenn記事執筆
6. デモ動画作成

## 📞 サポート情報

### 参考リンク
- [Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Next.js デプロイガイド](https://nextjs.org/docs/deployment)
- [FastAPI Dockerデプロイ](https://fastapi.tiangolo.com/deployment/docker/)

### トラブルシューティング
- ビルドエラー: 依存関係確認
- デプロイエラー: 権限・API有効化確認
- 動作不良: 環境変数・CORS設定確認
