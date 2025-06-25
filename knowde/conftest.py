"""pytest hooks."""

from neomodel import db

from knowde.primitive.config.env import Settings


def pytest_configure() -> None:
    """Pytest hook."""
    s = Settings()
    s.setup_db()


def pytest_runtest_teardown() -> None:
    """Pytest hook."""
    if db.driver is not None:
        s = Settings()
        s.terdown_db()
        db.clear_neo4j_database()


def pytest_sessionfinish() -> None:
    """Pytest hook."""
    s = Settings()
    s.terdown_db()
