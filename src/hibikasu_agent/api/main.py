from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hibikasu_agent.agents.parallel_orchestrator.agent import (
    create_parallel_review_agent,
)
from hibikasu_agent.api import ai_services
from hibikasu_agent.api.routers.reviews import router as reviews_router
from hibikasu_agent.api.schemas import Issue as ApiIssue
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


def _allowed_origins_from_env() -> list[str]:
    env_val = os.getenv("CORS_ALLOW_ORIGINS")
    if env_val:
        return [o.strip() for o in env_val.split(",") if o.strip()]
    # sensible defaults for local Next.js/Vite
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


# App assembly only; routers hold handlers
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    # Load .env if present for local development
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception as _err:
        _ = _err

    # Default: unconditionally inject ADK-backed review implementation
    try:
        logger.info("Initializing ADK parallel review agent (default)")
        model_name = os.getenv("ADK_MODEL") or "gemini-2.0-flash"
        agent = create_parallel_review_agent(model=model_name)
        app.state.adk_parallel_review_agent = agent

        def _adk_review_impl(prd_text: str) -> list[ApiIssue]:
            """Run ADK pipeline via Runner and return API Issue list.

            Uses InMemorySessionService and a one-off session. The merger agent writes
            FinalIssuesResponse under output_key "final_review_issues" in session state.
            """
            try:
                import asyncio
                from uuid import uuid4

                from google.adk.runners import Runner
                from google.adk.sessions import InMemorySessionService
                from google.genai import types as genai_types

                async def _run_once() -> list[dict]:
                    service = InMemorySessionService()
                    app_name = "hibikasu_review_api"
                    user_id = f"api_user_{uuid4()}"
                    session_id = f"sess_{uuid4()}"

                    # Create session
                    await service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

                    runner = Runner(agent=agent, app_name=app_name, session_service=service)

                    # Send PRD text as a single user message
                    content = genai_types.Content(role="user", parts=[genai_types.Part(text=str(prd_text))])

                    # Drain events until final; ignore intermediate
                    async for _event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                        pass

                    # Read aggregator output from session state
                    sess = await service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
                    state = getattr(sess, "state", {}) if sess else {}
                    out = state.get("final_review_issues") or {}
                    final_issues: list[dict] = []
                    if isinstance(out, dict) and isinstance(out.get("final_issues"), list):
                        final_issues = list(out.get("final_issues") or [])
                    return final_issues

                final_issues = asyncio.run(_run_once())

                api_issues: list[ApiIssue] = []
                for item in final_issues:
                    try:
                        api_issues.append(
                            ApiIssue(
                                issue_id=str(item.get("issue_id") or ""),
                                priority=int(item.get("priority") or 0),
                                agent_name=str(item.get("agent_name") or "unknown"),
                                comment=str(item.get("comment") or ""),
                                original_text=str(item.get("original_text") or ""),
                            )
                        )
                    except Exception as err:  # validation error on a single item
                        logger.warning("Skipping invalid ADK issue: %s | data=%s", err, item)
                return api_issues
            except Exception as err:
                # Try to surface nested ExceptionGroup/TaskGroup details if present
                detail = str(err)
                sub = getattr(err, "exceptions", None)
                if isinstance(sub, list | tuple) and sub:
                    detail = f"{detail} | first_sub={sub[0]}"
                logger.error("ADK review execution failed: %s", detail)
                return [
                    ApiIssue(
                        issue_id="AI-ERROR",
                        priority=1,
                        agent_name="AI-Orchestrator",
                        comment=f"ADK実行に失敗しました: {detail}",
                        original_text=str(prd_text)[:120] or "(empty)",
                    )
                ]

        ai_services.set_review_impl(_adk_review_impl)
    except Exception as err:
        logger.error("Failed to initialize ADK review integration: %s", err)

    yield


app: Any = FastAPI(title="Hibikasu PRD Reviewer API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(reviews_router)
