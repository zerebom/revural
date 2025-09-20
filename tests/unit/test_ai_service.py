from __future__ import annotations

import asyncio
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import hibikasu_agent.services.ai_service as ai_service_module
import pytest
from hibikasu_agent.api.schemas.reviews import Issue
from hibikasu_agent.constants.agents import AGENT_STATE_KEYS, SPECIALIST_AGENT_KEYS
from hibikasu_agent.services.ai_service import AiService


class _StubADK:
    async def run_review_async(
        self,
        prd_text: str,
        *,
        on_event: Callable[[Any], None] | None = None,
    ) -> list[Issue]:
        return [
            Issue(
                issue_id="UNIT-1",
                priority=1,
                agent_name="AI-Orchestrator",
                comment="unit review",
                original_text=prd_text,
            )
        ]

    async def answer_dialog_async(self, issue: Issue, question_text: str):  # type: ignore[no-untyped-def]
        return f"ans:{issue.issue_id}:{question_text}"


def test_kickoff_review_populates_session():
    svc = AiService(adk_service=_StubADK())
    rid = svc.new_review_session("PRD for unit test")
    # run background-style wrapper synchronously
    svc.kickoff_review(rid)
    data = svc.get_review_session(rid)
    assert data["status"] == "completed"
    assert isinstance(data["issues"], list)
    assert data["issues"][0].issue_id == "UNIT-1"


@pytest.mark.asyncio
async def test_answer_dialog_calls_provider():
    svc = AiService(adk_service=_StubADK())
    rid = svc.new_review_session("PRD for unit test")
    # kickoff_review is synchronous but uses asyncio.run internally; run it off the event loop.
    await asyncio.to_thread(svc.kickoff_review, rid)
    issue_id = svc.reviews_in_memory[rid].issues[0].issue_id  # type: ignore[index]

    out = await svc.answer_dialog(rid, issue_id, "Q?")
    assert out == f"ans:{issue_id}:Q?"


class _ErrorADK:
    async def run_review_async(self, prd_text: str, *, on_event=None):  # type: ignore[no-untyped-def]
        raise RuntimeError("ADK failed during aggregation")

    async def answer_dialog_async(self, issue: Issue, question_text: str):  # type: ignore[no-untyped-def]
        return ""


def test_kickoff_review_sets_failed_status_on_exception():
    svc = AiService(adk_service=_ErrorADK())
    rid = svc.new_review_session("PRD for unit test")

    svc.kickoff_review(rid)

    data = svc.get_review_session(rid)
    assert data["status"] == "failed"
    assert data["phase"] == "failed"
    assert "ADK failed during aggregation" in (data["phase_message"] or "")
    assert svc.reviews_in_memory[rid].error == "ADK failed during aggregation"


def test_handle_adk_event_updates_progress(monkeypatch):
    svc = AiService(adk_service=_StubADK())
    rid = svc.new_review_session("PRD for unit test")
    session = svc.reviews_in_memory[rid]
    first_agent, second_agent = SPECIALIST_AGENT_KEYS[:2]
    session.expected_agents = [first_agent, second_agent]

    state_key = AGENT_STATE_KEYS[first_agent]

    class DummyEvent:
        def __init__(self, delta: dict[str, object]):
            self.actions = SimpleNamespace(state_delta=delta)

    monkeypatch.setattr(ai_service_module, "ADKEvent", DummyEvent)

    svc._handle_adk_event(session, DummyEvent({state_key: {"final_issues": []}}))

    assert session.completed_agents == [first_agent]
    assert session.progress == 0.5
    assert session.phase_message.startswith("Engineer Specialist のレビューが完了しました")


def test_handle_adk_event_ignores_unknown_keys(monkeypatch):
    svc = AiService(adk_service=_StubADK())
    rid = svc.new_review_session("PRD for unit test")
    session = svc.reviews_in_memory[rid]
    session.expected_agents = [SPECIALIST_AGENT_KEYS[0]]

    class DummyEvent:
        def __init__(self, delta: dict[str, object]):
            self.actions = SimpleNamespace(state_delta=delta)

    monkeypatch.setattr(ai_service_module, "ADKEvent", DummyEvent)

    svc._handle_adk_event(session, DummyEvent({"unknown_state": {}}))

    assert session.completed_agents == []
    assert session.progress == 0.0
