#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import httpx


def post_json(client: httpx.Client, url: str, data: dict[str, Any]) -> dict[str, Any]:
    r = client.post(url, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def get_json(client: httpx.Client, url: str) -> dict[str, Any]:
    r = client.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def main() -> int:
    ap = argparse.ArgumentParser(description="Exercise Hibikasu PRD Reviewer API end-to-end.")
    ap.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    ap.add_argument(
        "--prd",
        default=("サンプルPRD: ダッシュボードの表示項目をユーザーがカスタマイズできる。"),
        help="PRD text to review",
    )
    ap.add_argument("--timeout", type=int, default=20, help="Polling timeout seconds")
    ap.add_argument("--interval", type=float, default=1.0, help="Polling interval seconds")
    ap.add_argument("--verbose", action="store_true", help="Print verbose responses")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    with httpx.Client(base_url=base) as client:
        # Start review
        res = post_json(client, "/reviews", {"prd_text": args.prd})
        rid = res.get("review_id")
        if not isinstance(rid, str):
            print("Failed to start review:", json.dumps(res, ensure_ascii=False), file=sys.stderr)
            return 1
        print(f"Started review: review_id={rid}")

        # Poll until completed or timeout
        deadline = time.time() + args.timeout
        status = "processing"
        issues: list[dict[str, Any]] | None = None
        while time.time() < deadline:
            body = get_json(client, f"/reviews/{rid}")
            status = body.get("status", "")
            issues = body.get("issues")
            print(f"Poll: status={status}")
            if status == "completed" and isinstance(issues, list) and issues:
                break
            time.sleep(args.interval)

        if status != "completed" or not issues:
            print("Timed out or no issues returned.", file=sys.stderr)
            if args.verbose:
                print(json.dumps({"status": status, "issues": issues}, ensure_ascii=False, indent=2))
            return 2

        first = issues[0]
        issue_id = first.get("issue_id", "")
        print(f"Completed. issues={len(issues)} first_issue_id={issue_id}")
        if args.verbose:
            print(json.dumps(first, ensure_ascii=False, indent=2))

        # Dialog
        dj = post_json(
            client,
            f"/reviews/{rid}/issues/{issue_id}/dialog",
            {"question_text": "この論点の背景と対策の根拠は？"},
        )
        print("Dialog:", dj.get("response_text", "(no text)"))

        # Suggest
        sj = post_json(client, f"/reviews/{rid}/issues/{issue_id}/suggest", {})
        print("Suggest: got target and suggestion")
        if args.verbose:
            print(json.dumps(sj, ensure_ascii=False, indent=2))

        # Apply suggestion
        aj = post_json(client, f"/reviews/{rid}/issues/{issue_id}/apply_suggestion", {})
        print("Apply:", aj.get("status"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
