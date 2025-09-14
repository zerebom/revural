# UI不具合修正計画書 (2025/09/14)

## 概要

現行実装で確認された3つの主要なUI不具合（優先度ロジック、色分け、相互連携の視認性）を完全に解決するための、詳細なフロントエンド修正方針書。

---

## 修正対象ファイルと作業順序

以下の順序で修正を進めることで、依存関係を解決し、効率的に実装を進めることができます。

1.  `frontend/lib/utils.ts` （**新規作成**）: 全体で利用する色分けのロジックを定義します。
2.  `frontend/components/ui/badge.tsx`: 優先度バッジの表示パターンを追加します。
3.  `frontend/components/review/IssueAccordionItem.tsx`: 優先度ロジックを修正し、色分けと選択状態を反映させます。
4.  `frontend/components/PrdTextView.tsx`: ハイライトの色分けと選択状態を反映させます。

---

### **1. 色マッピング関数の作成 (`frontend/lib/utils.ts`)**

-   **目的:** AIエージェント名とUIの色を紐付ける、一元的で再利用可能なロジックを作成する。
-   **AsIs:** 色分けのロジックがどこにも存在しない。
-   **ToBe:** `getAgentColorClasses(agentName)` を呼び出すと、そのエージェントに対応したTailwind CSSのクラス名セットが返ってくる状態。
-   **実装方針:**
    1.  `frontend/lib/` に `utils.ts` が存在することを確認し、なければ新規作成する。
    2.  以下の仕様で `getAgentColorClasses` 関数をエクスポートする。
        -   **入力:** `agent_name: string`
        -   **出力:** `{ bg: string; ring: string; border: string; }` という形状のオブジェクト。
        -   **ロジック:** `switch`文または `Map` を使用し、`agent_name` の文字列に応じて、以下のように定義済みのTailwind CSSクラスを返す。未知のエージェント名が来た場合は、汎用的なグレーを返すフォールバック処理を必ず実装する。

| エージェント名（例）        | `bg` (通常時)       | `bg` (選択時)       | `ring` (選択時)     | `border`          |
| --------------------------- | ------------------- | ------------------- | ------------------- | ----------------- |
| `UXレビューAI`              | `bg-blue-100`       | `bg-blue-200`       | `ring-blue-400`     | `border-blue-400` |
| `セキュリティレビューAI`    | `bg-red-100`        | `bg-red-200`        | `ring-red-400`      | `border-red-400`  |
| `QAレビューAI`                | `bg-green-100`      | `bg-green-200`      | `ring-green-400`    | `border-green-400`|
| `デフォルト（その他）`      | `bg-gray-100`       | `bg-gray-200`       | `ring-gray-400`     | `border-gray-400` |

---

### **2. 優先度バッジのバリアント追加 (`frontend/components/ui/badge.tsx`)**

-   **目的:** 優先度「中」を示すための"warning"バリアントを追加する。
-   **AsIs:** `destructive` (高) と `secondary` (低) のバリアントしか定義されていない。
-   **ToBe:** `variant="warning"` を指定すると、黄色系の警告色でバッジが表示される。
-   **実装方針:**
    -   `badgeVariants` (`cva`関数) の `variants.variant` オブジェクトに、`warning` プロパティを追加する。値は、例えば `"border-transparent bg-yellow-500 text-primary-foreground hover:bg-yellow-500/80"` のように設定する。

---

### **3. アコーディオン項目の修正 (`frontend/components/review/IssueAccordionItem.tsx`)**

-   **目的:** 優先度ロジックを修正し、エージェントごとの色分けと選択状態を明確に表示する。
-   **AsIs:** 優先度ロジックが逆。色分けがなく、どの項目が選択されているか不明。
-   **ToBe:** 正しい優先度が表示され、左端のボーダー色でエージェントが、背景色で選択状態が、一目でわかるUI。
-   **実装方針:**
    1.  **優先度ロジックの修正:** `priorityVariant` を決定する三項演算子を、`issue.priority === 1 ? "destructive" : issue.priority === 2 ? "warning" : "secondary"` というように、**数値が小さいほど優先度が高い**仕様に修正する。`as any`キャストは、前タスクの修正により不要になるため削除する。
    2.  **Truncate問題の修正:** サマリーテキストを囲む `div` (`className="flex-1 min-w-0"`) に `min-w-0` を追加し、テキストの省略が正しく機能するようにする。
    3.  **色分けと選択状態の反映:**
        -   コンポーネントの先頭で、`const colors = getAgentColorClasses(issue.agent_name);` のようにヘルパー関数を呼び出す。
        -   Zustandストアから `expandedIssueId` を取得し、`const isSelected = issue.issue_id === expandedIssueId;` という判定ロジックを追加する。
        -   ルート要素である `<AccordionItem>` に、`className` を追加し、`colors.border` を使って `border-l-4` の色を動的に設定する。
        -   `<AccordionTrigger>` に `className` を追加し、`isSelected` が `true` の場合に `colors.bg` (選択時) の背景色を適用する。

---

### **4. テキストハイライトの修正 (`frontend/components/PrdTextView.tsx`)**

-   **目的:** ハイライトの色をエージェントごとに変え、選択状態を明確にする。
-   **AsIs:** 全てのハイライトが黄色で、選択状態の変化がほとんど分からない。
-   **ToBe:** ハイライトがエージェントごとの色で表示される。クリックやアコーディオン展開で選択されたハイライトは、リング（枠線）が表示され、誰が見ても選択中だと分かる状態。
-   **実装方針:**
    1.  `react-markdown` の `components` プロパティで上書きしている `mark` コンポーネントのロジックを修正する。
    2.  `mark` コンポーネント内で、propsから渡ってくる `issue_id` を元に、対応する `issue` オブジェクトを `issues` 配列から検索する。
    3.  `const colors = getAgentColorClasses(foundIssue.agent_name);` のようにヘルパー関数を呼び出す。
    4.  `className` を生成するロジックを全面的に書き換える。
        -   `const isSelected = id && id === expandedIssueId;` は既存のものを流用。
        -   `clsx` や `tailwind-merge` といったユーティリティを使い、以下のようにクラスを動的に組み立てる。
            -   **基本スタイル:** `cursor-pointer rounded px-0.5`
            -   **通常時の色:** `colors.bg` (通常時)
            -   **選択時のスタイル:** `isSelected` が `true` の場合に、`colors.bg` (選択時) と `ring-2 ${colors.ring}` を適用する。
        -   これにより、選択されたハイライトは、他とは異なる濃い背景色とリングを持つ、明確に差別化された見た目になる。
