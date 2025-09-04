"""Basic smoke test to ensure the package can be imported."""

from hibikasu_agent import __version__
from hibikasu_agent.agents.specialist import create_specialist
from hibikasu_agent.schemas import Issue, ReviewSession
from hibikasu_agent.utils.logging_config import get_logger, setup_logging


def test_package_import() -> None:
    """Test that the main package can be imported."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_schemas_import() -> None:
    """Test that schema modules can be imported."""
    assert Issue is not None
    assert ReviewSession is not None


def test_agents_import() -> None:
    """Test that agent modules can be imported."""
    assert create_specialist is not None


def test_logging_import() -> None:
    """Test that logging utilities can be imported."""
    assert get_logger is not None
    assert setup_logging is not None
