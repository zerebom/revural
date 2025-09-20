from __future__ import annotations

import time

from hibikasu_agent.services.models import ReviewRuntimeSession
from hibikasu_agent.services.review_store import ReviewSessionStore


def _make_session() -> ReviewRuntimeSession:
    return ReviewRuntimeSession(
        created_at=time.time(),
        status="processing",
        issues=None,
        prd_text="",
        panel_type=None,
        progress=0.0,
        phase="processing",
        expected_agents=[],
        completed_agents=[],
    )


def test_review_store_create_and_get() -> None:
    store = ReviewSessionStore()
    session = _make_session()
    store.create("rid", session)

    fetched = store.get("rid")
    assert fetched is session


def test_review_store_mutate_and_remove() -> None:
    store = ReviewSessionStore()
    session = _make_session()
    store.create("rid", session)

    store.mutate("rid", lambda s: setattr(s, "progress", 0.5))
    assert store.get("rid").progress == 0.5

    # Mutating a missing session should be a no-op
    store.mutate("missing", lambda s: setattr(s, "progress", 1.0))

    store.remove("rid")
    assert store.get("rid") is None
