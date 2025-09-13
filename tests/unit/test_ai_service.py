from __future__ import annotations

import asyncio

from hibikasu_agent.api.schemas import Issue
from hibikasu_agent.services.ai_service import AiService


class _StubADK:
    async def run_review_async(self, prd_text: str):  # type: ignore[no-untyped-def]
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

    out = asyncio.get_event_loop().run_until_complete(svc.answer_dialog(rid, issue_id, "Q?"))
    assert out == f"ans:{issue_id}:Q?"
