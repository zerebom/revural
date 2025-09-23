# AIプロフィール表示項目仕様（改訂・コード非変更）

目的: 「人を指名してチームを編成する」体験を強化するため、プロフィール中心でシンプルなカード表示に統一する。

## 最小スキーマ（MVP）
- id: string 例) "engineer"（機械可読な安定ID。既存ロール: engineer / ux_designer / qa_tester / pm。将来: copywriter 等）
- name: string 例) "エンジニア スペシャリスト"（表示名。日本語名推奨）
- role_label: string 例) "エンジニアAI"（役割の日本語ラベル）
- avatarUrl?: string（なければイニシャル）
- bio?: string（約80文字目安・1文推奨）
- tags?: string[]（2〜3個まで。超過は「+n」表示）

> 既存コードは変更しない。バックエンドの `SPECIALIST_DEFINITIONS` はそのまま、UI層で上記のメタをマージして表示する想定。

## JSONサンプル（MVP想定）
```json
{
  "id": "copywriter",
  "name": "レオ・マルティネス",
  "role_label": "コピーライターAI",
  "avatarUrl": "/avatars/leo_martinez.png",
  "bio": "ブランドボイスを保ちながら、心に響くマイクロコピーを提案します。UXと成果に直結する言葉選びを支援。",
  "tags": ["#UXライティング", "#マイクロコピー", "#CTA改善"]
}
```

## 表示ルール（カード）
- ヘッダー: 大きめ Avatar/イニシャル + name + 「選択中」Badge
- サブ: bio（約80文字・最大2行）。全文はHoverでツールチップ可
- フッター: tags 2〜3個 + 「+n」
- アクセスビリティ: `button` としてフォーカスリング、`aria-pressed` で選択状態を表現

## 文言ガイド
- name: 日本語名を基本。人物名風・役割名どちらでも可
- bio: 約80文字・1文で専門性と貢献が伝わる。箇条書きや長文は避ける
- tags: 具体的な観点/得意領域。英数字/和文混在可、`#` は任意
- role_label: 役割の和名（例: 「プロダクトマネージャーAI」「UXデザイナーAI」）

## データ供給の方針（コード非変更）
- 既存のロール定義は `src/hibikasu_agent/constants/agents.py` の `SPECIALIST_DEFINITIONS` を使用
- 追加メタ（name/role_label/bio/tags/avatarUrl）は TOML などの外部設定から読み込み、UIで結合表示（将来 `GET /agents/profiles` で配信可能）
- 互換: メタが無い場合は `display_name`/`review_description` のサブセットでフォールバック表示

## 枚数と密度（レイアウト指針）
- 1行あたり3〜4枚（レスポンシブ）。高さは固定しカードが揃うように
- スクロール圧が高い場合は検索/フィルタ（chips）を上部に配置（「タグ中心」は補助として活用）

## DoD（この仕様の完了条件）
- 上記スキーマの項目が存在すれば表示し、無ければ自然に省略
- bio は約80文字で要点が伝わる。tags は最大3個に留め「+n」表記に切り替わる
- コード（型定義）は変更しない
