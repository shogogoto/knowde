"""pytest hooks."""
from neomodel import clear_neo4j_database, db, install_all_labels


def pytest_configure() -> None:
    """Pytest hook."""
    install_all_labels()


def pytest_runtest_teardown() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)


def pytest_sessionfinish() -> None:
    """Pytest hook."""
    if db.driver is not None:
        clear_neo4j_database(db)
        db.driver.close()
        db.close_connection()
