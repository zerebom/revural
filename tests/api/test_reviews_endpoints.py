from __future__ import annotations


def test_post_reviews_and_poll_until_completed(client):
    # Start a review
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    assert res.status_code == 200
    review_id = res.json()["review_id"]
    assert isinstance(review_id, str) and review_id

    # Poll until completed, with a timeout
    import time

    for _ in range(10):  # max 1 sec
        r = client.get(f"/reviews/{review_id}")
        assert r.status_code == 200
        body = r.json()
        if body["status"] == "completed":
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Review did not complete in time")

    assert body["status"] == "completed"
    assert isinstance(body.get("issues"), list)
    assert len(body["issues"]) >= 1
    # Validate issue shape without relying on specific IDs
    first = body["issues"][0]
    assert set(["issue_id", "priority", "agent_name", "comment", "original_text"]).issubset(first.keys())
