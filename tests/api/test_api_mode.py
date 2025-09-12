import os

from hibikasu_agent.api import ai_services


def test_default_mode_is_mock(monkeypatch, client_ai_mode):
    # Ensure default mode (no env) behaves like mock and returns completed by second poll
    monkeypatch.delenv("HIBIKASU_API_MODE", raising=False)
    monkeypatch.delenv("ENABLE_AI", raising=False)

    client = client_ai_mode

    res = client.post("/reviews", json={"prd_text": "テストPRD"})
    rid = res.json()["review_id"]

    r1 = client.get(f"/reviews/{rid}")
    assert r1.status_code == 200

    r2 = client.get(f"/reviews/{rid}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] in ("processing", "completed")


def test_ai_mode_uses_ai_services(monkeypatch, client_ai_mode):
    # Switch to ai mode
    monkeypatch.setenv("HIBIKASU_API_MODE", "ai")

    # Inject deterministic AI review implementation
    def fake_impl(prd_text: str):
        return [
            {
                "issue_id": "TST-1",
                "priority": 1,
                "agent_name": "AI-Orchestrator",
                "comment": "fake review",
                "original_text": prd_text,
            }
        ]

    # Convert dicts to Issue via the service call path
    def impl(prd_text: str):
        return [ai_services.Issue(**d) for d in fake_impl(prd_text)]

    ai_services.set_review_impl(impl)

    client = client_ai_mode

    res = client.post("/reviews", json={"prd_text": "AI-PRD"})
    rid = res.json()["review_id"]

    # first poll: processing
    r1 = client.get(f"/reviews/{rid}")
    assert r1.json()["status"] == "processing"

    # second poll: should be completed by ai_services
    r2 = client.get(f"/reviews/{rid}")
    body = r2.json()
    assert body["status"] == "completed"
    assert body["issues"] and body["issues"][0]["issue_id"] == "TST-1"
