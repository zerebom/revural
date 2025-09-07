from __future__ import annotations

from fastapi.testclient import TestClient
from hibikasu_agent.api.main import app


def test_post_reviews_and_poll_until_completed():
    client = TestClient(app)

    # Start a review
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    assert res.status_code == 200
    review_id = res.json()["review_id"]
    assert isinstance(review_id, str) and review_id

    # First poll -> processing
    r1 = client.get(f"/reviews/{review_id}")
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["status"] in ("processing", "completed")

    # Second poll -> should be completed with issues from injected impl
    r2 = client.get(f"/reviews/{review_id}")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["status"] == "completed"
    assert isinstance(body2.get("issues"), list)
    assert len(body2["issues"]) >= 1
    assert body2["issues"][0]["issue_id"] == "TST-1"
