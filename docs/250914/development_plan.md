# AI文書レビューツール アップデート計画 (2025/09/14)

## 概要

ユーザーストーリーマップに基づき、アプリケーションのUI/UXを根本的に刷新するための開発計画。
開発は3つのマイルストーンに分割して進める。各タスクには、開発者が参照すべきファイルや現状(AsIs)、目指すべき姿(ToBe)を詳細に記載する。

**関連ドキュメント:**
-   [ユーザーストーリーマップ](./../user_story_map.md)
-   [UI/UXフロー定義](./../ui_ux_flow.md)
-   [現状アーキテクチャ](./current_architecture.md)

---

## マイルストーン 1: 新UI基盤の構築（トリアージ体験の実現）

**ゴール:** ユーザーストーリーマップのStep 2を達成し、新しいレビュー画面の骨格を構築する。右ペインを「全指摘一覧のアコーディオン形式」UIに刷新する。

**開発の進め方と注意点:**
-   **前提条件:** このマイルストーンのフロントエンド開発は、バックエンドの「**データモデルの拡張**」タスク（`FinalIssue`に`summary`フィールド追加）が完了し、APIが新しいデータ構造を返す状態になっていることを前提に進めるのが最も効率的です。
-   **完了の定義:**
    -   レビュー結果画面の右ペインが、全指摘を一覧表示するアコーディオンUIになっている。
    -   アコーディオンを開閉すると、左ペインの該当箇所が自動でスクロール＆ハイライトされる。
    -   左ペインの文書はMarkdownとしてレンダリングされている。
-   **テスト方針:**
    -   各新規コンポーネント（`IssueListView`, `IssueAccordionItem`）については、Storybookで様々なパターンの`issue`データを渡して表示崩れがないか確認することを推奨します。
    -   インタラクション（アコーディオン開閉とスクロールの連動）については、VitestとReact Testing Libraryを用いたユニットテストで動作を保証することが望ましいです。

---

### Frontend タスク

#### **1. ディレクトリ構造の整理**

-   **目的:** 新しいUIコンポーネントの置き場所を準備し、既存コードとの責務分離を明確にする。
-   **AsIs:** レビュー画面関連のコンポーネント(`IssueDetailView.tsx`, `IssueCard.tsx`など)が `frontend/components/` 直下に配置されている。
-   **ToBe:** 新しいレビュー画面のコンポーネント群を `frontend/components/review/` に集約し、既存コンポーネントは `legacy` ディレクトリに退避させる。
-   **手順:**
    1.  `mkdir -p frontend/components/review/legacy` を実行する。
    2.  `mv frontend/components/IssueDetailView.tsx frontend/components/review/legacy/` を実行。
    3.  `mv frontend/components/IssueCard.tsx frontend/components/review/legacy/` を実行。
    4.  `mv frontend/components/ChatWindow.tsx frontend/components/review/legacy/` を実行。
    5.  `mv frontend/components/SuggestionBox.tsx frontend/components/review/legacy/` を実行。

---

#### **2. 新規コンポーネントの作成**

-   **目的:** 右ペインに表示する「指摘一覧アコーディオン」UIの雛形を作成する。
-   **参考情報:**
    -   `shadcn/ui` のAccordionコンポーネント: [https://ui.shadcn.com/docs/components/accordion](https://ui.shadcn.com/docs/components/accordion)
    -   Issueの型定義: `frontend/lib/types.ts`
-   **方針:**
    1.  まず、`frontend/components/review/` に `IssueListView.tsx` を作成する。このコンポーネントは `issues` 配列をpropsとして受け取り、`map` を使って各 `issue` を `IssueAccordionItem` コンポーネント（次に作成）として描画する責務を持つ。内部では `shadcn/ui` の `<Accordion>` をルート要素として使用する。
    2.  次に、`frontend/components/review/` に `IssueAccordionItem.tsx` を作成する。これは個々の指摘事項を表示するアコーディオン項目となる。
        -   `shadcn/ui` の `<AccordionItem>` をベースにする。
        -   `<AccordionTrigger>` には、指摘のサマリーテキスト、担当エージェント名、優先度を示す `<Badge>` を配置する。レイアウトにはFlexboxを使い、テキストが長い場合は `truncate` で省略されるようにする。
        -   `<AccordionContent>` には、指摘の全文と、「AIに質問する」ボタンを配置する。このボタンの具体的な実装はマイルストーン2で行う。

---

#### **3. 状態管理 (Zustand) の更新**

-   **目的:** どの指摘アコーディオンが開かれているかをグローバルに管理できるようにする。
-   **参照ファイル:** `frontend/store/useReviewStore.ts`
-   **AsIs:** `selectedIssueId` が選択中の指摘IDを管理している。この命名は、UIの主役が「左ペインのハイライト選択」であった頃の名残。
-   **ToBe:** 新しいUIでは、ユーザー操作の起点が「右ペインのアコーディオン開閉」に変わるため、その役割をより正確に表す `expandedIssueId` という名前に変更する。
-   **方針:**
    -   `frontend/store/useReviewStore.ts` を開き、`ReviewState` interfaceと `create` 内の初期ステートにおいて、`selectedIssueId` を `expandedIssueId` にリネームする。
    -   同様に、セッターである `setSelectedIssueId` も `setExpandedIssueId` にリネームする。アプリケーション全体で、このリネームに伴う参照エラーを修正していく。

---

#### **4. メインレビューページの改修**

-   **目的:** 古い詳細表示コンポーネントを、新しく作成した指摘一覧コンポーネントに置き換える。
-   **参照ファイル:** `frontend/components/ReviewPage.tsx`, `frontend/app/reviews/[id]/page.tsx`
-   **AsIs:** `ReviewPage.tsx` は `PrdTextView` と `IssueDetailView` (旧)を左右に並べている。
-   **ToBe:** `ReviewPage.tsx` の右ペインを、新しく作成した `IssueListView` に差し替える。
-   **方針:**
    1.  まず `frontend/app/reviews/[id]/page.tsx` で、前タスクでリネームした `useReviewStore` の `expandedIssueId` を参照するように修正する。
    2.  `frontend/components/ReviewPage.tsx` を開き、右ペインを描画している部分の `IssueDetailView` (旧コンポーネント)への参照を削除する。
    3.  代わりに、新しく作成した `IssueListView` をインポートし、配置する。`issues` 配列をpropsとして渡す。

---

#### **5. インタラクションの実装**

-   **目的:** 右ペインのアコーディオン開閉と、左ペインの自動スクロール＆ハイライトを連動させる。
-   **参照ファイル:** `frontend/components/review/IssueListView.tsx`, `frontend/components/PrdTextView.tsx`
-   **AsIs:** 左ペインのハイライトクリックで右ペインが更新される一方向の連携。
-   **ToBe:** 右ペインのアコーディオン操作を起点として、左ペインが追従する双方向の連携を実現する。
-   **方針:**
    1.  **右→左の連携:** `IssueListView.tsx` を修正する。`shadcn/ui` の `<Accordion>` コンポーネントは、`value` propsで現在開いているアイテムのIDを制御し、`onValueChange` propsでユーザーが開閉操作をしたことを通知する。これらを利用して、Zustandの `expandedIssueId` とアコーディオンの状態を双方向にバインドする。
    2.  **左→右の連携:** `PrdTextView.tsx` 内でハイライト (`<mark>`) がクリックされた際の `onSelect` ハンドラは、Zustandの `setExpandedIssueId` を呼び出す。これにより、1のバインディングを通じて対応するアコーディオンが自動的に開く。
    3.  **自動スクロール:** `PrdTextView.tsx` に `useEffect` フックを追加する。このフックは `expandedIssueId` (props経由で渡ってくる) の変更を監視する。変更が検知されたら、対応する `issue_id` を持つハイライト要素 (`<mark>`) をDOMから探し出し、その要素に対して `scrollIntoView({ behavior: 'smooth', block: 'center' })` を呼び出す。対象要素を特定しやすくするため、`<mark>` 要素に `data-issue-id={p.issue_id}` のようなカスタムデータ属性を付与しておくと良い。

---

#### **6. バグ修正: ハイライト位置の精度向上**

-   **目的:** `span` のインデックス計算ロジックを見直し、特にマルチバイト文字が含まれる場合にハイライトがずれる問題を修正する。
-   **関連タスク:** このタスクは後続の「**7. Markdownレンダリングのサポート**」と密接に関連します。Markdownの構文木を扱う過程で文字位置の計算方法が変わる可能性があるため、並行して調査・実装を進めることが望ましいです。
-   **参照ファイル:** `frontend/components/PrdTextView.tsx`
-   **AsIs:** `prdText.slice(start, end)` というJavaScriptの文字列操作に依存しており、文字コードの扱いによってはバックエンドの計算とずれが生じる可能性がある。
-   **ToBe:** バックエンドとフロントエンドで文字インデックスの計算方法を統一するか、より堅牢な方法でハイライトを実現する。
-   **調査・実装方針:**
    -   **原因調査:** まず、ハイライトがずれる具体的なテキストパターン（特定の漢字や絵文字など）を特定する。
    -   **バックエンド確認:** バックエンド（Python）がどのように文字インデックスを計算しているか確認する。Pythonの `len()` やスライスは、フロントエンドのJavaScriptと挙動が異なる場合がある。
    -   **解決策の検討:**
        -   **案A (推奨):** バックエンドから `span` のインデックスではなく、ハイライト対象の **テキストそのもの (`original_text`)** を基準に処理する。フロントエンドでは `prdText.indexOf(issue.original_text)` を使って位置を特定する。ただし、同一テキストが複数ある場合に問題となる可能性があるため、一意性のあるアンカーを追加するなどの工夫が必要。
        -   **案B:** バックエンドとフロントエンドで、文字インデックスの計算ライブラリを統一する（例: `grapheme-splitter`など）。

---

-   **[ ] 7. Markdownレンダリングのサポート**
    -   **目的:** 左ペインの文書表示エリアでMarkdown記法を解釈し、リッチテキストとして表示することで、ユーザーの可読性を向上させる。
    -   **参照ファイル:** `frontend/components/PrdTextView.tsx`
    -   **AsIs:** Markdownテキストがただのプレーンテキストとして表示され、見出しやリストなどの構造が失われている。
    -   **ToBe:** GitHubのプレビューのようにMarkdownがレンダリングされ、かつAIによる指摘箇所は正確にハイライトされる。
    -   **技術選定に関する補足:**
        -   **ライブラリ:** `unified`, `remark`, `remark-react` のエコシステムは非常に強力ですが、バージョン間の互換性問題が発生しやすいため、導入時は `package.json` のバージョンを固定し、最小限のプラグイン構成から始めることを推奨します。
        -   **セキュリティ:** ユーザー入力をHTMLとして描画するため、XSS（クロスサイトスクリプティング）のリスクを考慮する必要があります。`rehype-sanitize` などのサニタイズ用プラグインを導入し、意図しないスクリプトの実行をブロックする設定を必ず行ってください。
    -   **方針（推奨: 構文木へのハイライト情報注入）:**
        1.  **構文木への変換:** `unified` や `remark` といったライブラリを導入し、Markdownテキストを構文木（AST）に変換する。この構文木の各ノードは、元のテキスト内での位置情報を持っている。
        2.  **ハイライト情報の注入:** AIからの指摘が示す文字範囲 (`span`) と、構文木ノードの位置情報を照合する。指摘箇所に該当するノードを見つけ、構文木を直接操作して「ハイライトすべき」という印（カスタムノード）を木構造に追加する。
        3.  **Reactコンポーネントへの描画:** `remark-react` のようなライブラリを使い、ハイライトの印がついたカスタム構文木をReactコンポーネントに変換する。「ハイライトの印」はカスタムの `<mark>` コンポーネントに、その他のMarkdown要素は `<h1>`, `<li>` などに対応するHTMLタグとしてレンダリングする。

-   **[ ] 8. レビュワーごとのハイライト色分け**
    -   **目的:** 指摘箇所と指摘リストの項目を視覚的に結びつけ、ユーザーが「誰の指摘か」を直感的に識別できるようにする。
    -   **参照ファイル:** `frontend/components/PrdTextView.tsx`, `frontend/components/review/IssueAccordionItem.tsx`
    -   **AsIs:** 全てのハイライトが同じ色で表示されるため、どの指摘が誰のものか区別がつきにくい。
    -   **ToBe:** AIエージェントごとに異なる色が割り当てられ、左ペインのハイライトと右ペインのアコーディオンヘッダーが同じ色で表示される。
    -   **方針:**
        1.  **色マッピング定義:** `lib/utils.ts` などに、`agent_name` をキーとして対応するTailwind CSSの色クラス（例: `bg-yellow-200`, `bg-blue-200`）を返すヘルパー関数を作成する。
        2.  **ハイライトへの適用:** `PrdTextView` 内で `<mark>` タグをレンダリングする際に、このヘルパー関数を使って動的にクラス名を付与する。
        3.  **アコーディオンへの適用:** `IssueAccordionItem` のヘッダー部分に、同じヘルパー関数を使って取得した色で、ボーダーやアイコンなどの視覚的なインジケーターを追加する。

### Backend タスク

#### **アーキテクチャに関する重要事項 (リファクタリング提案)**

コードレビューの結果、現在の実装には将来の技術的負債に繋がりかねない設計上の課題が発見されました。マイルストーン2の実装と並行して、以下の点の改善を強く推奨します。

-   **1. Issueモデルの一本化:**
    -   **現状の課題:** `api/schemas/reviews.py` の `Issue` と `schemas/models.py` の `FinalIssue` という、ほぼ同じ責務を持つ2つのモデルが混在しており、データの信頼性(Single Source of Truth)を損なっています。
    -   **推奨アクション:** これら2つのモデルを一つに統合し、アプリケーション全体で単一のIssueモデルを参照するようにリファクタリングする。これにより、意図しないデータの不整合や変換ロジックの複雑化を防ぎます。

-   **2. APIリクエストの厳格なバリデーション:**
    -   **現状の課題:** ステータス更新APIが受け取る`status`が単なる文字列(`str`)のため、不正な値を受け入れてしまう可能性があります。
    -   **推奨アクション:** `typing.Literal`を使用し、`"pending"`, `"done"`など、受け入れ可能な値を明示的に定義する。これにより、API層で不正なリクエストを自動的に弾くことができます。

---

1.  **[ ] データモデル拡張:**
    -   **ファイル:** `src/hibikasu_agent/schemas/models.py`
    -   **目的:** `FinalIssue` モデルに、指摘の進捗を管理するための `status` フィールドを追加する。

2.  **[ ] APIスキーマ追加:**
    -   **参照ファイル:** `src/hibikasu_agent/api/schemas/reviews.py`
    -   **やること:** ステータス更新APIが通信で使うデータ形式を定義する。具体的には、リクエストボディ用に`status`フィールドを持つ`UpdateStatusRequest`モデルと、レスポンス用に`status: Literal["success", "failed"]`を持つ`UpdateStatusResponse`モデルの2つを、Pydanticモデルとして追加する。

3.  **[ ] サービス層インターフェース更新:**
    -   **参照ファイル:** `src/hibikasu_agent/services/base.py`
    -   **やること:** `AbstractReviewService`クラスに、`review_id`, `issue_id`, `status`を引数に取り、成否を`bool`で返す`update_issue_status`という名前の抽象メソッドを追加する。

4.  **[ ] サービス層実装:**
    -   **参照ファイル:** `src/hibikasu_agent/services/mock_service.py`
    -   **やること:** `MockService`クラスに`update_issue_status`メソッドを実装する。このメソッドは、`self._store`から該当のセッションとIssueを探索し、ステータスを更新するロジックを記述する。
    -   **注意点:** `MockService`が保持している`Issue`の型と、`status`を持つべき`FinalIssue`の型に不整合がある点に留意して実装する。まずはスタブ実装でも可。

5.  **[ ] APIエンドポイント作成:**
    -   **参照ファイル:** `src/hibikasu_agent/api/routers/reviews.py`
    -   **やること:** `@router.patch`デコレータを使用して、`/reviews/{review_id}/issues/{issue_id}/status`というパスでリクエストを受け付けるエンドポイント関数を新規に追加する。この関数は、リクエストボディを受け取り、サービス層の`update_issue_status`メソッドを呼び出して、その結果をレスポンスとして返す。

---

## マイルストーン 2: 対話体験の深化と状態管理

**ゴール:** マイルストーン1の基盤の上に、Step 3で定義された「深掘り」の体験を追加する。

### Frontend タスク

#### 1. `IssueDetailView` (深掘りビュー) のレイアウト構築

-   **目的:** 深掘りビューにおける「チャットエリアが狭い」というUI課題を解決する。チャットの高さを最大限確保しつつ、必要な時には議論の文脈も参照できる、バランスの取れたUIを実現する。
-   **UI/UX方針 (アコーディオン方式):**
    -   指摘の要約や対象テキストといった**コンテキスト情報を、折りたたみ可能なアコーディオン内に格納**する。
    -   ユーザーがビューを開いた**初期状態では、アコーディオンは閉じており**、チャットエリアが広く表示される。
    -   ユーザーが議論の文脈を再確認したい時だけ、アコーディオンを展開して詳細を閲覧する。
    -   アコーディオンのヘッダーには常に指摘の要約を表示し、ビュー全体の文脈が失われないように配慮する。
-   **参照ファイル:** `components/review/IssueDetailView.tsx` (新規作成)
-   **やること:**
    -   `shadcn/ui`の`Accordion`コンポーネントを使い、上記の方針に基づいたコンテキストエリアを実装する。
    -   アコーディオンの下に、チャットUIとアクションボタンを配置するメインエリアを設ける。

#### 2. `Vercel AI Elements` 導入とチャットUIの刷新

-   **目的:** 既存のチャットUIを、より高機能でデザイン性の高い`Vercel AI Elements`ベースのものにアップグレードし、対話体験を向上させる。
-   **参照ライブラリ:** https://ai-sdk.dev/elements/overview
-   **やること:**
    -   `npx ai-elements@latest` コマンドを参考に、`Vercel AI Elements`をプロジェクトに導入する。
    -   `IssueDetailView.tsx`内に、`Vercel AI Elements`の`Conversation`, `Message`, `PromptInput`を組み合わせて、新しいチャットUIを構築する。
    -   既存のAPI連携ロジック（メッセージの送受信）を、新しいUIに接続する。

#### 3. 状態管理 (Zustand) とパネル切り替えロジックの実装

-   **目的:** リストビューと、新しく構築する`IssueDetailView`（深掘りビュー）との間の画面遷移を、状態管理を通じて制御する。
-   **参照ファイル:** `frontend/store/useReviewStore.ts`, `frontend/components/ReviewPage.tsx`
-   **やること:**
    -   `useReviewStore`に、現在の表示モードを管理する`viewMode: 'list' | 'detail'`の状態を追加する。
    -   `ReviewPage.tsx`でこの`viewMode`を監視し、表示するコンポーネントを動的に切り替えるロジックを実装する。

#### 4. UI/UXの微調整 (アニメーションとトランジション)

-   **目的:** 画面遷移やUI要素の動きをスムーズにすることで、アプリケーションの操作感を向上させ、より洗練された印象を与える。
-   **やること:**
    -   `framer-motion`やCSSトランジションを利用し、`ReviewPage.tsx`でのリストビューと深掘りビューの切り替え時に、パネルが横からスライドイン/アウトするようなアニメーションを実装する。
    -   `IssueDetailView.tsx`内のアコーディオンが開閉する際のアニメーションが自然に見えるように調整する。

#### 5. 品質の向上 (型定義の強化とテスト)

-   **目的:** フロントエンドコードの堅牢性を高め、将来の機能追加やリファクタリングに備える。
-   **やること:**
    -   Zustandストア(`useReviewStore.ts`)のステートとアクションに、より厳密な型定義を適用する。
    -   `Vitest`と`React Testing Library`を使用し、`useReviewStore`の各アクションが意図通りにステートを更新するかのユニットテストを作成する。特に`setViewMode`や`updateIssueStatus`といった重要なアクションを対象とする。

### Backend タスク

#### **アーキテクチャに関する重要事項 (リファクタリング提案)**

コードレビューの結果、現在の実装には将来の技術的負債に繋がりかねない設計上の課題が発見されました。マイルストーン2の実装と並行して、以下の点の改善を強く推奨します。

-   **1. Issueモデルの一本化:**
    -   **現状の課題:** `api/schemas/reviews.py` の `Issue` と `schemas/models.py` の `FinalIssue` という、ほぼ同じ責務を持つ2つのモデルが混在しており、データの信頼性(Single Source of Truth)を損なっています。
    -   **推奨アクション:** これら2つのモデルを一つに統合し、アプリケーション全体で単一のIssueモデルを参照するようにリファクタリングする。これにより、意図しないデータの不整合や変換ロジックの複雑化を防ぎます。

-   **2. APIリクエストの厳格なバリデーション:**
    -   **現状の課題:** ステータス更新APIが受け取る`status`が単なる文字列(`str`)のため、不正な値を受け入れてしまう可能性があります。
    -   **推奨アクション:** `typing.Literal`を使用し、`"pending"`, `"done"`など、受け入れ可能な値を明示的に定義する。これにより、API層で不正なリクエストを自動的に弾くことができます。

---

1.  **[ ] データモデル拡張:**
    -   **ファイル:** `src/hibikasu_agent/schemas/models.py`
    -   **目的:** `FinalIssue` モデルに、指摘の進捗を管理するための `status` フィールドを追加する。

2.  **[ ] APIスキーマ追加:**
    -   **ファイル:** `src/hibikasu_agent/api/schemas/reviews.py`
    -   **目的:** ステータス更新APIが通信で使うデータ形式（リクエストとレスポンス）を定義する。
    -   **参照ファイル:** `src/hibikasu_agent/api/schemas/reviews.py`
    -   **手順:** `ApplySuggestionResponse`の後などに、以下の2つのPydanticモデルを追加する。
        ```python
        class UpdateStatusRequest(BaseModel):
            status: str

        class UpdateStatusResponse(BaseModel):
            status: Literal["success", "failed"]
        ```

3.  **[ ] サービス層インターフェース更新:**
    -   **ファイル:** `src/hibikasu_agent/services/base.py`
    -   **目的:** `AbstractReviewService` に、ステータス更新機能の共通インターフェース（抽象メソッド）を追加し、責務を明確にする。
    -   **参照ファイル:** `src/hibikasu_agent/services/base.py`
    -   **手順:** `AbstractReviewService`クラス内に、以下の抽象メソッド定義を追加する。
        ```python
        @abstractmethod
        def update_issue_status(self, review_id: str, issue_id: str, status: str) -> bool:
            """Updates the status of a specific issue and returns success."""
            raise NotImplementedError
        ```

4.  **[ ] サービス層実装:**
    -   **ファイル:** `src/hibikasu_agent/services/mock_service.py`
    -   **目的:** `AbstractReviewService` の新しいインターフェースを実装する。インメモリ上のデータを実際に更新するロジックをここに追加する。
    -   **参照ファイル:** `src/hibikasu_agent/services/mock_service.py`
    -   **課題:** `MockService`が保持する`Issue`モデル(`api.schemas.Issue`)と、`status`を持つ`FinalIssue`モデル(`schemas.models.FinalIssue`)の間に不整合がある。このタスクではまず動作するスタブを実装し、この不整合の解消は別途検討する。
    -   **手順:** `MockService`クラス内に、以下のメソッドを実装する。
        ```python
        def update_issue_status(self, review_id: str, issue_id: str, status: str) -> bool:
            session = self._store.get(review_id)
            if not session or not session.issues:
                return False

            # キャストとモデルの不整合に注意
            issues: list[Issue] = cast("list[Issue]", session.issues)

            for issue in issues:
                if issue.issue_id == issue_id:
                    # TODO: モデルの不整合を解消し、実際の更新処理を実装する
                    # issue.status = status のようなコードを書きたいが、型が異なる
                    print(f"Issue {issue_id} status updated to {status} (mock)")
                    return True
            return False
        ```

5.  **[ ] APIエンドポイント作成:**
    -   **ファイル:** `src/hibikasu_agent/api/routers/reviews.py`
    -   **目的:** フロントエンドからのステータス更新リクエストを受け付けるための `PATCH` エンドポイントを新規に作成する。
    -   **参照ファイル:** `src/hibikasu_agent/api/routers/reviews.py`
    -   **手順:**
        1.  `UpdateStatusRequest`, `UpdateStatusResponse` を`...api.schemas`からインポートする。
        2.  ファイル下部に以下のエンドポイントを追加する。
        ```python
        @router.patch(
            "/reviews/{review_id}/issues/{issue_id}/status",
            response_model=UpdateStatusResponse,
        )
        def update_issue_status_endpoint(
            review_id: str,
            issue_id: str,
            req: UpdateStatusRequest,
            service: AbstractReviewService = Depends(get_review_service),
        ) -> UpdateStatusResponse:
            success = service.update_issue_status(review_id, issue_id, req.status)
            if not success:
                raise HTTPException(status_code=404, detail="Issue not found")
            return UpdateStatusResponse(status="success")
        ```

---

## マイルストーン 3: 体験の拡充（レビュー依頼とサマリー）

**ゴール:** コア体験の前後のStep 1とStep 4を実装し、全体の体験を完成させる。

### Frontend タスク

-   **[ ] 1. レビュー依頼フォームの強化**
    -   `components/PrdInputForm.tsx` に、`shadcn/ui` の `Select` や `RadioGroup` を使って「文書タイプ」や「レビュー観点」の選択UIを追加する。
-   **[ ] 2. サマリーページの作成**
    -   `app/reviews/[id]/summary/page.tsx` を新規作成。
    -   統計情報（指摘総数、ステータス別件数など）を表示するUIを作成。
    -   全指摘とチャット履歴を一覧表示するUIを作成。
-   **[ ] 3. エクスポート機能の実装**
    -   サマリーページに「Markdownとしてエクスポート」「クリップボードにコピー」ボタンを設置。
    -   レビュー結果全体をMarkdown形式の文字列に変換するロジックを実装する。
-   **[ ] 4. 全体的なUI/UX改善**
    -   `components/layout/Header.tsx` のような共通ヘッダーコンポーネントを作成し、ナビゲーションを配置する。
    -   アプリケーション全体で `shadcn/ui` のコンポーネント利用を徹底し、デザインの一貫性を高める。

### Backend タスク

-   **[ ] 1. APIの修正 (レビュー依頼)**
    -   `POST /reviews` エンドポイントを修正し、「文書タイプ」や「レビュー観点」をリクエストボディで受け取れるようにする。
    -   受け取ったパラメータに応じて、レビューを実行するAIエージェントの種類やプロンプトを切り替えるロジックを実装する。
-   **[ ] 2. APIの新規作成 (サマリー)**
    -   `GET /reviews/{review_id}/summary` のような、サマリー表示に必要な情報をまとめて返すエンドポイントを新規に作成することを検討する。（既存の `GET /reviews/{review_id}` でも代用可能か要件次第）
-   **[ ] 3. ファイルアップロード機能**
    -   `POST /reviews/upload` のような、ファイルアップロードを受け付けるエンドポイントを新規に作成する。
    -   アップロードされたファイル（.md, .docxなど）をパースしてテキストを抽出するライブラリを導入する。
