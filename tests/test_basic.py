"""Basic smoke test to ensure the package can be imported."""


def test_package_import() -> None:
    """Test that the main package can be imported."""
    from hibikasu_agent import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)


def test_schemas_import() -> None:
    """Test that schema modules can be imported."""
    from hibikasu_agent.schemas import Persona, ProjectSettings

    assert Persona is not None
    assert ProjectSettings is not None


def test_agents_import() -> None:
    """Test that agent modules can be imported."""
    from hibikasu_agent.agents.persona_agent import PersonaAgent

    assert PersonaAgent is not None


def test_logging_import() -> None:
    """Test that logging utilities can be imported."""
    from hibikasu_agent.utils.logging_config import get_logger, setup_logging

    assert get_logger is not None
    assert setup_logging is not None
