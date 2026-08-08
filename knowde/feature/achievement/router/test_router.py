"""test router."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.conftest import mark_async_test


@pytest.fixture
def client() -> TestClient:
    """Test client."""
    return TestClient(root_router())


@mark_async_test()
async def test_archievement_history(client: TestClient):  # noqa: D103, RUF029
    res = client.post("/user/archievement-history", json={"user_ids": []})
    assert res.status_code == status.HTTP_200_OK
