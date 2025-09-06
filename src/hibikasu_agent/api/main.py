from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app: Any = FastAPI(title="Hibikasu PRD Reviewer API (Mock)", version="0.1.0-mock")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(reviews_router)
