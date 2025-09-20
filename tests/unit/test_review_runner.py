from __future__ import annotations

import pytest
from hibikasu_agent.api.schemas.reviews import Issue
from hibikasu_agent.services.review_runner import AdkReviewRunner


class _StubADKService:
    def __init__(self) -> None:
        self.calls = 0

    async def run_review_async(self, prd_text: str, *, on_event=None):  # type: ignore[no-untyped-def]
        self.calls += 1
        if on_event:
            on_event(object())
        return [
            Issue(
                issue_id="ID-1",
                priority=1,
                agent_name="engineer_specialist",
                summary="summary",
                comment="comment",
                original_text=prd_text,
            )
        ]


@pytest.mark.asyncio
async def test_review_runner_run_async_returns_issues() -> None:
    stub = _StubADKService()
    runner = AdkReviewRunner(stub)

    issues = await runner.run_async("prd text")

    assert len(issues) == 1
    assert stub.calls == 1


def test_review_runner_run_blocking_uses_async_version() -> None:
    stub = _StubADKService()
    runner = AdkReviewRunner(stub)

    issues = runner.run_blocking("prd text")

    assert len(issues) == 1
    assert stub.calls == 1
