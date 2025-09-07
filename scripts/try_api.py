#!/usr/bin/env python3
from __future__ import annotations

import json
import time

import requests

# FastAPIサーバーのアドレス
BASE_URL = "http://127.0.0.1:8000"

# テスト用のPRDテキスト (prd.mdから抜粋)
PRD_TEXT = """
次期スプリントで開発予定の「ダッシュボードのカスタマイズ機能」に関するPRDドラフト。
ユーザーはダッシュボードの表示項目を自由にカスタマイズし、その設定を保存できる。
"""


def main():
    """APIのレビューフローをテストするメイン関数"""
    headers = {"Content-Type": "application/json"}

    # --- 1. POST /reviews ---
    print("🚀 1. Starting a new review session...")
    post_payload = {"prd_text": PRD_TEXT, "panel_type": "Webサービス"}
    try:
        response = requests.post(f"{BASE_URL}/reviews", headers=headers, data=json.dumps(post_payload))
        response.raise_for_status()  # エラーがあれば例外を発生させる
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling POST /reviews: {e}")
        print("Is the FastAPI server running? -> uvicorn src.hibikasu_agent.api.main:app --reload")
        return

    review_id = response.json()["review_id"]
    print(f"✅ Review session started. review_id: {review_id}\n")

    # --- 2. GET /reviews/{review_id} (Polling) ---
    print(f"⏳ 2. Polling for results for review_id: {review_id}")

    max_polls = 20  # 最大20回ポーリング (合計60秒)
    for i in range(max_polls):
        try:
            print(f"   - Polling attempt {i + 1}/{max_polls}...")
            get_url = f"{BASE_URL}/reviews/{review_id}"
            response = requests.get(get_url)
            response.raise_for_status()

            data = response.json()
            status = data.get("status")

            if status == "completed":
                print("\n✅ Review completed!")
                print("✨ Final Issues:")
                # 結果を綺麗に表示
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # --- 3. POST /dialog on the first issue ---
                issues = data.get("issues") or []
                if issues:
                    first_issue = issues[0]
                    issue_id = first_issue.get("issue_id")
                    q = "この論点の背景と対策の優先度を簡潔に教えてください"
                    print("\n🗣️  3. Asking dialog about the first issue...")
                    dj = requests.post(
                        f"{BASE_URL}/reviews/{review_id}/issues/{issue_id}/dialog",
                        headers=headers,
                        data=json.dumps({"question_text": q}),
                    )
                    if dj.ok:
                        print("💬 Dialog response:")
                        print(json.dumps(dj.json(), indent=2, ensure_ascii=False))
                    else:
                        print(f"❌ Dialog failed: {dj.status_code} {dj.text}")
                return

            if status == "failed":
                print("\n❌ Review failed on the server.")
                print("Server response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return

            # "processing" の場合は待機してリトライ
            time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error during polling: {e}")
            return

    print("\n❌ Polling timed out. The review took too long to complete.")


if __name__ == "__main__":
    main()
