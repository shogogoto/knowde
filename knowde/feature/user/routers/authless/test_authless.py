"""authless test."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.feature.user.repo.label import LUser
from knowde.feature.user.routers import user_router


@pytest.fixture
def client() -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(user_router())
    return TestClient(api)


def test_search_user_by_name(client: TestClient):
    """名前で検索."""
    LUser(uid="10", email="u1@example.com", display_name="aaa").save()
    LUser(uid="12", email="u2@example.com", display_name="bbb").save()
    LUser(uid="13", email="u3@example.com", display_name="ccc").save()
    LUser(uid="14", email="u4@example.com", display_name="ddd").save()

    res = client.get("/user/search/", params={"name": "a"})
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get("/user/search/", params={"name": "a"})  # 大文字小文字は区別しない
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get("/user/search/", params={"id": "1"})  # 大文字小文字は区別しない
    assert len(res.json()) == 4  # noqa: PLR2004
