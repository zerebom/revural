from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hibikasu_agent.api.routers.reviews import router as reviews_router
from hibikasu_agent.core.config import settings
from hibikasu_agent.utils.logging_config import get_logger, set_log_level

logger = get_logger(__name__)


# App assembly only; routers hold handlers
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    # Set package logger level without disrupting uvicorn handlers
    try:
        pkg_logger = logging.getLogger("hibikasu_agent")
        set_log_level(pkg_logger, settings.hibikasu_log_level)
        # Ensure our package logger emits to stdout even when uvicorn config
        # doesn't attach handlers to the root logger.
        if not pkg_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            level = getattr(logging, settings.hibikasu_log_level.upper(), logging.INFO)
            handler.setLevel(level)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            pkg_logger.addHandler(handler)
            # Avoid duplicate emission via root if it gets a handler later
            pkg_logger.propagate = False
    except Exception as _err:
        _ = _err

    # ADK-backed review installation is handled by providers/DI as needed

    yield


app: Any = FastAPI(title="Hibikasu PRD Reviewer API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=settings.cors_allow_origin_regex_or_none,
)

# Routers
app.include_router(reviews_router)
