# バグ修正計画 (2025/09/20)

## 前提と背景
- 本プロジェクトは個人開発でユーザーは不在。ただし既存コードで `span` はバックエンド側が再計算しており、この前提は維持する。
- `span` を返さない指摘でも内容自体は有益なため、失敗した場合は `span=None` のまま保持する。
- 目標は `span` の再計算成功率と優先度ロジックの品質向上。

---

## 1. span が None になる問題

### 現状の把握
- ADK からは `original_text` しか返らず、`span` は `utils/span_calculator.py` が `prd_text` から探索して算出している。
- 現行実装は空白除去など単純な一致判定しか持たず、微小な表現差で失敗して `None` になっている。

### 修正方針
1. **正規化の強化** (`utils/span_calculator.py`)
   - `unicodedata.normalize("NFKC", text)` で全角半角を統一。
   - 小文字化・不要記号トリムなど軽処理を加える。
2. **曖昧一致の導入**
   - `difflib.SequenceMatcher` などで `original_text` と `prd_text` の最長一致を探索。
   - マッチ率 (`ratio`) に閾値（例: 0.6）を設け、閾値未満の場合は `None` を返す。
3. **位置復元の改善**
   - 正規化後のインデックスを元の文字列の位置へマッピングするヘルパーを見直す（既存 `_find_normalized_start_index` 等を再利用しつつ改良）。
4. **フォールバック**
   - まずは既存の単純検索を試み、失敗した場合に曖昧一致を行う。

### 実装タスク
- [ ] `utils/span_calculator.py` に上記ロジックを実装。
- [ ] `services/mappers/api_issue_mapper.py` では `calculate_span(prd_text, original_text)` の呼び出しを継続し、結果が `None` でもそのまま `ApiIssue` に渡す。
- [ ] フロントエンドで `span` が `None` の場合はハイライトを描画せず、カードは表示する運用を確認。

### テスト
- [ ] `tests/unit/utils/test_span_calculator.py` に以下のケースを追加：
  - 表記ゆれ（句読点違い、全角/半角、改行差）でも位置を捉えられる。
  - マッチ率が閾値未満のパターンでは `None` となる。
- [ ] `tests/unit/services/test_api_issue_mapper.py` で `span=None` も受け入れることを確認。

---

## 2. priority が連番になる問題

### 現状の把握
- `_calculate_issue_priorities` が severity でソート後、`enumerate` で連番を振っているため、同じ重要度でも重複しない番号になっている。

### 修正方針
- `severity -> priority` の固定マッピング（例: `{"High": 1, "Mid": 2, "Low": 3}`）で決定する。
- リストの順序は当面既存仕様のままでも良いが、必要に応じて `severity` で安定ソートする。

### 実装タスク
- [ ] `_calculate_issue_priorities` を書き換え、`enumerate` を廃止。
- [ ] `FinalIssue.priority` はマッピング結果を設定し、重複を許容。

### テスト
- [ ] `tests/unit/test_tools.py` を更新し、`priority` が期待どおり `1/2/3` の重複値になることを確認。

---

## 3. 動作確認
- [ ] `pytest tests/unit -q`
- [ ] ローカルフロントエンドでハイライト有無・優先度表示を確認。

---

## 補足
- 将来的に ADK が span を返すようになった場合は、本計算をスキップできるようフックを用意しておくと良い。
- span 取得に失敗した指摘が多い場合はログを整備し、どのような表現差が原因か把握できるようにする。
