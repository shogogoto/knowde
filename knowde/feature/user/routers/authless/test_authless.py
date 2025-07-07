"""authless test."""

from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.feature.user.routers import user_router
from knowde.shared.labels.user import LUser


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
    LUser(uid="99", email="u5@example.com", display_name="eee").save()

    res = client.get("/user/search/", params={"name": "a"})
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get("/user/search/", params={"name": "A"})  # 大文字小文字は区別しない
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get("/user/search/", params={"id": "1"})  # 大文字小文字は区別しない
    assert len(res.json()) == 4  # noqa: PLR2004

    res = client.get("/user/search/")
    assert len(res.json()) == 5  # noqa: PLR2004


def test_search_uuid_hyphenless_or_not(client: TestClient):
    """ハイフンの有無に関わらずUUIDで検索できる."""
    u = LUser(email="u1@example.com", display_name="aaa").save()
    res = client.get("/user/search/", params={"id": u.uid})
    assert len(res.json()) == 1

    res = client.get("/user/search/", params={"id": str(UUID(u.uid))})
    assert len(res.json()) == 1
