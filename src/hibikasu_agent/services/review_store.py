"""In-memory store for review runtime sessions."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping

from hibikasu_agent.services.models import ReviewRuntimeSession


class ReviewSessionStore:
    """Encapsulates in-memory management of ``ReviewRuntimeSession`` instances."""

    def __init__(self) -> None:
        self._sessions: dict[str, ReviewRuntimeSession] = {}

    def create(self, review_id: str, session: ReviewRuntimeSession) -> None:
        """Persist a newly created review session."""

        self._sessions[review_id] = session

    def get(self, review_id: str) -> ReviewRuntimeSession | None:
        """Retrieve a session by identifier."""

        return self._sessions.get(review_id)

    def update(self, review_id: str, session: ReviewRuntimeSession) -> None:
        """Replace an existing session instance."""

        self._sessions[review_id] = session

    def remove(self, review_id: str) -> None:
        """Remove a session if present."""

        self._sessions.pop(review_id, None)

    def mutate(self, review_id: str, fn: Callable[[ReviewRuntimeSession], None]) -> None:
        """Apply an in-place mutation callback when the session exists."""

        session = self.get(review_id)
        if session is not None:
            fn(session)

    def as_dict(self) -> MutableMapping[str, ReviewRuntimeSession]:
        """Expose the backing mapping for read-only scenarios."""

        return self._sessions
