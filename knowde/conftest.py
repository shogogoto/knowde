"""pytest hooks."""


from neomodel import clear_neo4j_database, config, db


def pytest_configure() -> None:
    """Pytest hook."""
    config.AUTO_INSTALL_LABELS = True


def pytest_runtest_teardown() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)
        db.close_connection()


def pytest_collection_finish() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)
        db.close_connection()
