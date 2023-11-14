"""pytest hooks."""


import os

from neomodel import config, db


def pytest_configure() -> None:
    """Run before tests."""
    config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
    config.AUTO_INSTALL_LABELS = True


def pytest_collection_finish() -> None:
    """Run after tests."""
    db.close_connection()
