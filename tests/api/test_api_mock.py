from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_start_review_returns_review_id():
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    assert res.status_code == 200
    body = res.json()
    assert "review_id" in body and isinstance(body["review_id"], str)


def test_polling_transitions_to_completed_and_returns_issues():
    # start
    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    review_id = res.json()["review_id"]

    # first poll -> processing
    r1 = client.get(f"/reviews/{review_id}")
    assert r1.status_code == 200
    assert r1.json()["status"] in ("processing", "completed")

    # second poll -> completed with issues
    r2 = client.get(f"/reviews/{review_id}")
    assert r2.status_code == 200
    data = r2.json()
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
