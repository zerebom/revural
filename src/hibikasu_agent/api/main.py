from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hibikasu_agent.api.dependencies import _use_ai_mode
from hibikasu_agent.api.routers.reviews import router as reviews_router
from hibikasu_agent.core.config import settings
from hibikasu_agent.services.ai_service import AiService
from hibikasu_agent.services.providers.adk import ADKService
from hibikasu_agent.utils.logging_config import get_logger, setup_application_logging

logger = get_logger(__name__)


# App assembly only; routers hold handlers
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    # Configure application/package logging
    setup_application_logging(settings.hibikasu_log_level)

    # Initialize ADK provider once if running in AI mode
    if _use_ai_mode():
        try:
            adk_service = ADKService()
            app.state.adk_service = adk_service
            app.state.ai_service = AiService(adk_service=adk_service)
            logger.info("ADKService and AiService initialized in app.state")
        except Exception as err:  # nosec B110
            # Do not crash app; requests will see failure when trying to use AI mode
            logger.error("Failed to initialize AI services", extra={"error": str(err)})

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
