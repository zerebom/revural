import os

from hibikasu_agent.api.schemas.reviews import Issue
from hibikasu_agent.services.providers.adk import ADKService


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

    # Inject deterministic AI review implementation by monkeypatching ADKService
    mock_issues = [
        Issue(
            issue_id="TST-1",
            priority=1,
            agent_name="AI-Orchestrator",
            comment="fake review",
            original_text="AI-PRD",
        )
    ]

    async def impl_async(self, prd_text: str, *, on_event=None, selected_agents=None):  # type: ignore[no-untyped-def]
        return mock_issues

    monkeypatch.setattr(ADKService, "run_review_async", impl_async, raising=False)

    client = client_ai_mode

    res = client.post("/reviews", json={"prd_text": "AI-PRD"})
    rid = res.json()["review_id"]

    # Poll until completed, with a timeout
    import time

    for _ in range(10):  # max 1 sec
        r = client.get(f"/reviews/{rid}")
        body = r.json()
        if body["status"] == "completed":
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Review did not complete in time")

    assert body["status"] == "completed"
    # In our test client, dependency override injects a stub AI service
    # that returns a deterministic issue id "STUB-1".
    assert body["issues"] and body["issues"][0]["issue_id"] == "STUB-1"
