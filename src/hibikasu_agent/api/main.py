from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hibikasu_agent.api.routers.reviews import router as reviews_router
from hibikasu_agent.services.providers.adk import install_default_review_impl
from hibikasu_agent.utils.logging_config import get_logger, set_log_level

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


def _allowed_origin_regex_from_env() -> str | None:
    r"""Optional regex string for CORS allow_origin_regex.

    Set CORS_ALLOW_ORIGIN_REGEX to a Python-style regex, e.g.:
    ^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?$
    """
    regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX")
    return regex if regex else None


# App assembly only; routers hold handlers
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    # Set package logger level without disrupting uvicorn handlers
    try:
        pkg_logger = logging.getLogger("hibikasu_agent")
        set_log_level(pkg_logger, os.getenv("HIBIKASU_LOG_LEVEL", "INFO"))
        # Ensure our package logger emits to stdout even when uvicorn config
        # doesn't attach handlers to the root logger.
        if not pkg_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            level = getattr(logging, os.getenv("HIBIKASU_LOG_LEVEL", "INFO").upper(), logging.INFO)
            handler.setLevel(level)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            pkg_logger.addHandler(handler)
            # Avoid duplicate emission via root if it gets a handler later
            pkg_logger.propagate = False
    except Exception as _err:
        _ = _err

    # Load .env if present for local development
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception as _err:
        _ = _err

    # Default: delegate ADK-backed review installation to providers layer
    install_default_review_impl(app)

    yield


app: Any = FastAPI(title="Hibikasu PRD Reviewer API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=_allowed_origin_regex_from_env(),
)

# Routers
app.include_router(reviews_router)
