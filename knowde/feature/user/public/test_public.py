"""authless test."""

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.user.routers import user_router
from knowde.shared.user.label import LUser
from knowde.shared.user.schema import UserReadPublic


@async_fixture()
def client() -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(user_router())
    return TestClient(api)


@mark_async_test()
async def test_search_user_by_name(client: TestClient):
    """名前で検索."""
    await LUser(email="u1@example.com", display_name="aaa").save()
    await LUser(email="u2@example.com", display_name="bbb").save()
    await LUser(email="u3@example.com", display_name="ccc").save()
    await LUser(email="u4@example.com", display_name="ddd").save()
    await LUser(email="u5@example.com", display_name="eee").save()

    res = client.post("/user/search/", data={"q": "a"})
    assert len(res.json()) == 1


@mark_async_test()
async def test_get_user_profile(client: TestClient):
    """ユーザーをusername または id で検索できる."""
    await LUser(email="u1@example.com", username="aaa").save()
    res = client.get("/user/profile/a")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    res = client.get("/user/profile/aaa")
    assert res.is_success
    u = UserReadPublic.model_validate(res.json())
    assert u.username == "aaa"
