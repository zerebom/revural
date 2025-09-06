from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hibikasu_agent.api import config
from hibikasu_agent.api.routers.reviews import router as reviews_router


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
    # Optionally initialize orchestrator runner and inject into ai_services
    if config.is_ai_mode() and os.getenv("HIBIKASU_AI_REVIEW_IMPL", "").strip().lower() == "orchestrator":
        try:
            from google.adk.runners import InMemoryRunner

            from hibikasu_agent.agents.parallel_orchestrator.agent import (
                create_parallel_review_agent,
            )
            from hibikasu_agent.api import ai_services
            from hibikasu_agent.api.ai_orchestrator_bridge import (
                make_review_impl_from_runner,
            )

            pipeline = create_parallel_review_agent()
            runner = InMemoryRunner(agent=pipeline, app_name="prd_review_pipeline")
            app.state.orchestrator_runner = runner

            # Override AI review implementation to reuse initialized runner
            ai_services.set_review_impl(make_review_impl_from_runner(runner))
        except Exception as _err:
            # If initialization fails, continue with default impl (mock or AI fallback)
            _ = _err
    yield


app: Any = FastAPI(title="Hibikasu PRD Reviewer API (Mock)", version="0.1.0-mock", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(reviews_router)
