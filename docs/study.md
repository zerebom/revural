# FastAPI開発の学び

このドキュメントは、`hibikasu-agent`プロジェクトの開発過程で得られたFastAPIに関する知見や調査結果をまとめたものです。

---
## FastAPI: mypyの `untyped decorator` 警告を回避する2つの方法

FastAPIでAPIエンドポイントを定義する際、`@app.get()` のようなデコレータを使用するのが一般的です。しかし、`mypy`のような静的型チェッカーを厳密な設定で利用していると、`error: "App" has no attribute "get"; maybe "add_api_route"?` や `untyped decorator` といった警告に遭遇することがあります。

これは、FastAPIインスタンスの型推論が`mypy`にうまく伝わっていない場合に発生します。この問題を解決し、型安全性を保つための方法を2つ記録します。

### 方法1: `app.add_api_route()` を使用する（現在のプロジェクトでの採用方式）

これは、デコレータ構文の代替としてFastAPIが提供しているルーティング登録方法です。

**実装例:** (`src/hibikasu_agent/api/main.py`で採用)

```python
from fastapi import FastAPI
from typing import Any

# FastAPIインスタンスの型を `Any` と宣言
app: Any = FastAPI(...)

# エンドポイントとなる関数を定義
async def get_review(review_id: str) -> StatusResponse:
    # ...処理...
    return StatusResponse(...)

# app.add_api_route() を使って関数をパスに紐付け
app.add_api_route(
    "/reviews/{review_id}",
    get_review,
    methods=["GET"],
    response_model=StatusResponse
)
```

**長所:**
- `app`変数の型を`Any`とすることで、`mypy`のデコレータに関する型チェックを意図的に回避できるため、警告を確実に抑制できます。
- FastAPIのコア機能であり、信頼性が高いです。

**短所:**
- FastAPIの最も一般的で直感的な書き方であるデコレータが使えず、コードの可読性が若干低下します。
- 関数の定義とルーティングの定義が離れてしまうため、コードの関連性が分かりにくくなることがあります。

### 方法2: `app` の型を `FastAPI` と明示する（モダンな推奨方式）

よりモダンで一般的に推奨される方法は、FastAPIインスタンスの型を`mypy`に正しく伝えることです。

**実装例:**

```python
from fastapi import FastAPI

# FastAPIインスタンスの型を `FastAPI` と明示的に宣言
app: FastAPI = FastAPI(...)

# デコレータを使ってエンドポイントを直感的に定義
@app.get("/reviews/{review_id}", response_model=StatusResponse)
async def get_review(review_id: str) -> StatusResponse:
    # ...処理...
    return StatusResponse(...)
```

**長所:**
- FastAPIの標準的で直感的なデコレータ構文が使え、コードが非常にクリーンで読みやすくなります。
- 関数の定義とその公開パスが一箇所にまとまるため、コードの意図が明確になります。
- `app`変数が正しく型付けされるため、エディタの補完機能などがより正確に動作します。

**短所:**
- プロジェクトの`mypy`設定によっては、この形式でも稀に型関連の問題が起きる可能性がゼロではありませんが、ほとんどのケースで問題なく動作します。

### まとめ

`hibikasu-agent` プロジェクトでは、一度「方法2」へのリファクタリングを行いましたが、チームの方針と安定性を考慮し、現在は「方法1」の `app.add_api_route()` を使う方式を採用しています。

しかし、将来的にFastAPIや`mypy`のバージョンアップで状況が変わったり、新規プロジェクトを立ち上げたりする際には、「方法2」のデコレータ形式が、より可読性とメンテナンス性の高いコードを実現するための第一の選択肢となるでしょう。
