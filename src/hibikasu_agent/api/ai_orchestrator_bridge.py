from __future__ import annotations

from typing import TYPE_CHECKING

from hibikasu_agent.api.schemas import Issue

if TYPE_CHECKING:
    from collections.abc import Callable


def load_review_impl() -> Callable[[str], list[Issue]]:
    """Attempt to load an orchestrator-backed review implementation.

    Returns a callable taking PRD text and producing a list[Issue].
    If orchestrator dependencies are unavailable, raises ImportError.
    """
    try:
        # Lazy imports to avoid import costs in non-AI environments
        from google.adk.runners import InMemoryRunner
        from google.genai import types

        from hibikasu_agent.agents.parallel_orchestrator.agent import (
            create_parallel_review_agent,
        )
    except Exception as e:  # pragma: no cover - exercised only with ADK present
        raise ImportError("Orchestrator dependencies not available") from e

    pipeline = create_parallel_review_agent()
    runner = InMemoryRunner(agent=pipeline, app_name="prd_review_pipeline")

    async def _run(prd_text: str) -> list[Issue]:  # pragma: no cover
        session_id = "review_session"
        user_id = "system"
        await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
        message = types.Content(parts=[types.Part(text=prd_text)], role="user")
        events = []
        async for ev in runner.run_async(session_id=session_id, user_id=user_id, new_message=message):
            events.append(ev)
        # Expect pipeline merger to emit final_review_issues; map to Issues
        # Fallback: empty list
        issues: list[Issue] = []
        try:
            payload = getattr(events[-1], "content", None) or {}
            data = getattr(payload, "data", None) or {}
            final = data.get("final_review_issues") or data
            for it in final.get("final_issues") or final.get("issues") or []:
                issues.append(
                    Issue(
                        issue_id=str(it.get("issue_id") or ""),
                        priority=int(it.get("priority") or 0),
                        agent_name=str(it.get("agent_name") or ""),
                        comment=str(it.get("comment") or ""),
                        original_text=str(it.get("original_text") or ""),
                    )
                )
        except Exception as e:  # log-friendly placeholder without leaking secrets
            # Swallow errors in bridge; return empty issues for resilience
            _ = e
        return issues

    # Adapter to sync callable from async implementation
    def review_impl(prd_text: str) -> list[Issue]:  # pragma: no cover
        import anyio

        result = anyio.run(_run, prd_text)
        if isinstance(result, list):
            return result
        try:
            return list(result)
        except Exception:
            return []

    return review_impl
