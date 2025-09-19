from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from hibikasu_agent.api.schemas import Issue
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


def test_answer_dialog_calls_provider():
    svc = AiService(adk_service=_StubADK())
    rid = svc.new_review_session("PRD for unit test")
    svc.kickoff_review(rid)
    issue_id = svc.reviews_in_memory[rid].issues[0].issue_id  # type: ignore[index]

    out = asyncio.run(svc.answer_dialog(rid, issue_id, "Q?"))
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
