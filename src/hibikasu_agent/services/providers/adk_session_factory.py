"""Factory for creating ADK runner/session contexts."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


@dataclass
class AdkSessionContext:
    app_name: str
    user_id: str
    session_id: str
    session_service: InMemorySessionService
    runner: Runner


class AdkSessionFactory:
    def __init__(self, app_name: str = "hibikasu_review_api") -> None:
        self._app_name = app_name

    async def create_session(self, agent) -> AdkSessionContext:  # type: ignore[no-untyped-def]
        """Build a runner and session service bound to unique identifiers."""

        session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
        user_id = f"api_user_{uuid4()}"
        session_id = f"sess_{uuid4()}"

        await session_service.create_session(
            app_name=self._app_name,
            user_id=user_id,
            session_id=session_id,
        )
        runner = Runner(agent=agent, app_name=self._app_name, session_service=session_service)
        return AdkSessionContext(
            app_name=self._app_name,
            user_id=user_id,
            session_id=session_id,
            session_service=session_service,
            runner=runner,
        )
