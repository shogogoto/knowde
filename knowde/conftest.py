"""pytest hooks."""

import os

from neomodel import clear_neo4j_database, config, db, install_all_labels


def pytest_configure() -> None:
    """Pytest hook."""
    config.DATABASE_URL = os.environ["NEO4J_URL"]
    install_all_labels()


def pytest_runtest_teardown() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)


def pytest_sessionfinish() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)
        db.close_connection()
