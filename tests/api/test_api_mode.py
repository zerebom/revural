import os

from hibikasu_agent.api.schemas import Issue
from hibikasu_agent.services.providers import adk


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

    # Inject deterministic AI review implementation by monkeypatching ADK runner
    def impl(prd_text: str):
        return [
            Issue(
                issue_id="TST-1",
                priority=1,
                agent_name="AI-Orchestrator",
                comment="fake review",
                original_text=prd_text,
            )
        ]

    monkeypatch.setattr(adk, "run_review", impl, raising=False)

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
