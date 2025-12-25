"""quiz router test."""

# from knowde.conftest import mark_async_test

from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.fixture import fx_u
from knowde.shared.user.label import LUser


def client() -> TestClient:
    """Test client."""
    return TestClient(root_router())


u = async_fixture()(fx_u)


@mark_async_test()
async def test_sent2term_seq(u: LUser):
    """単文から用語を当てるクイズの一連の流れ."""
