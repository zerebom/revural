from __future__ import annotations


def test_post_reviews_and_poll_until_completed(client):
    # Start a review
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    assert res.status_code == 200
    review_id = res.json()["review_id"]
    assert isinstance(review_id, str) and review_id

    # First poll -> processing or completed
    r1 = client.get(f"/reviews/{review_id}")
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["status"] in ("processing", "completed")

    # Second poll -> should be completed with mock issues
    r2 = client.get(f"/reviews/{review_id}")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["status"] == "completed"
    assert isinstance(body2.get("issues"), list)
    assert len(body2["issues"]) >= 1
    # Validate issue shape without relying on specific IDs
    first = body2["issues"][0]
    assert set(["issue_id", "priority", "agent_name", "comment", "original_text"]).issubset(first.keys())
