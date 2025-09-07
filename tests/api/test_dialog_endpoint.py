from __future__ import annotations

from fastapi.testclient import TestClient
from hibikasu_agent.api.main import app


def test_issue_dialog_returns_response_text():
    client = TestClient(app)

    # Start review and get review_id
    res = client.post("/reviews", json={"prd_text": "テストPRD（対話テスト）"})
    assert res.status_code == 200
    review_id = res.json()["review_id"]

    # First poll: processing
    r1 = client.get(f"/reviews/{review_id}")
    assert r1.status_code == 200

    # Second poll: completed with issues from injected impl
    r2 = client.get(f"/reviews/{review_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "completed"
    issue_id = body["issues"][0]["issue_id"]

    # Ask dialog
    q = "この論点の背景を教えてください"
    dj = client.post(
        f"/reviews/{review_id}/issues/{issue_id}/dialog",
        json={"question_text": q},
    )
    assert dj.status_code == 200
    data = dj.json()
    assert "response_text" in data and isinstance(data["response_text"], str)
    assert data["response_text"] != ""


def test_issue_dialog_returns_404_when_issue_not_found():
    client = TestClient(app)

    # Start review
    res = client.post("/reviews", json={"prd_text": "テストPRD（対話404）"})
    review_id = res.json()["review_id"]

    # Ensure session exists by polling once
    client.get(f"/reviews/{review_id}")

    # Use a non-existent issue id
    dj = client.post(
        f"/reviews/{review_id}/issues/NO_SUCH_ISSUE/dialog",
        json={"question_text": "存在しない論点？"},
    )
    assert dj.status_code == 404
