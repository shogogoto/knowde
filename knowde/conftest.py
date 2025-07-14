"""pytest hooks."""

from collections.abc import Callable, Generator

import pytest
import pytest_asyncio
from neomodel import db
from neomodel.async_.core import AsyncDatabase

from knowde.api.middleware.logging.log_config import clear_logging, setup_logging
from knowde.config.env import Settings


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


_mark_async_test = pytest.mark.asyncio(loop_scope="session")
mark_async_session_auto_fixture = pytest_asyncio.fixture(
    loop_scope="session",
    scope="session",
    autouse=True,
)
mark_async_function_auto_fixture = pytest_asyncio.fixture(
    loop_scope="session",
    autouse=True,
)
# mark_sync_session_auto_fixture = pytest.fixture(scope="session", autouse=True)
# mark_sync_function_auto_fixture = pytest.fixture(autouse=True)


def async_fixture() -> Callable:  # noqa: D103
    return mark_async_function_auto_fixture


def mark_async_test() -> Callable:  # noqa: D103
    return _mark_async_test


# @pytest_asyncio.fixture(loop_scope="function")
# async def teardown():
#     """非同期テストの後片付け."""
#     yield


@mark_async_function_auto_fixture
async def setup():  # noqa: D103
    await AsyncDatabase().clear_neo4j_database()
    yield
    await AsyncDatabase().close_connection()


@pytest.fixture(autouse=True)
def control_app_logging(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Enable application logging for tests marked with 'enable_app_logging'."""
    marker = request.node.get_closest_marker("enable_app_logging")
    if marker is None:
        yield
        return
    setup_logging()
    yield
    clear_logging()
