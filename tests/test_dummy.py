"""Basic smoke test to ensure the package can be imported."""

from hibikasu_agent import __version__
from hibikasu_agent.core.example import ExampleConfig


def test_package_import() -> None:
    """Test that the main package can be imported."""
    assert __version__ is not None


def test_core_module_import() -> None:
    """Test that core modules can be imported."""
    assert ExampleConfig is not None
