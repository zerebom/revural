from __future__ import annotations


def test_start_review_returns_review_id(client):
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    assert res.status_code == 200
    body = res.json()
    assert "review_id" in body and isinstance(body["review_id"], str)


def test_polling_transitions_to_completed_and_returns_issues(client):
    # start
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    review_id = res.json()["review_id"]

    # The mock service completes synchronously
    r = client.get(f"/reviews/{review_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert isinstance(data["issues"], list) and len(data["issues"]) >= 1
    issue_id = data["issues"][0]["issue_id"]

    # dialog
    d = client.post(
        f"/reviews/{review_id}/issues/{issue_id}/dialog",
        json={"question_text": "なぜ問題ですか？"},
    )
    assert d.status_code == 200
    assert "response_text" in d.json()

    # suggest
    s = client.post(f"/reviews/{review_id}/issues/{issue_id}/suggest")
    assert s.status_code == 200
    sj = s.json()
    assert "suggested_text" in sj and "target_text" in sj

    # apply suggestion
    a = client.post(f"/reviews/{review_id}/issues/{issue_id}/apply_suggestion")
    assert a.status_code == 200
    assert a.json()["status"] == "success"
