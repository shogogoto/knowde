"""pytest hooks."""


from neomodel import clear_neo4j_database, db

from knowde.feature.__core__.config import Settings


def pytest_configure() -> None:
    """Pytest hook."""
    s = Settings()
    s.setup_db()


def pytest_runtest_teardown() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)


def pytest_sessionfinish() -> None:
    """Pytest hook."""
    s = Settings()
    s.terdown_db()
