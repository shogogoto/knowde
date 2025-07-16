"""authless test."""

from uuid import UUID

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
    await LUser(uid="10", email="u1@example.com", display_name="aaa").save()
    await LUser(uid="12", email="u2@example.com", display_name="bbb").save()
    await LUser(uid="13", email="u3@example.com", display_name="ccc").save()
    await LUser(uid="14", email="u4@example.com", display_name="ddd").save()
    await LUser(uid="99", email="u5@example.com", display_name="eee").save()

    res = client.get("/user/search/", params={"display_name": "a"})
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get(
        "/user/search/",
        params={"display_name": "A"},
    )  # 大文字小文字は区別しない
    assert len(res.json()) == 1
    assert res.json()[0]["display_name"] == "aaa"

    res = client.get("/user/search/", params={"id": "1"})  # 大文字小文字は区別しない
    assert len(res.json()) == 4  # noqa: PLR2004

    res = client.get("/user/search/")
    assert len(res.json()) == 5  # noqa: PLR2004


@mark_async_test()
async def test_search_uuid_hyphenless_or_not(client: TestClient):
    """ハイフンの有無に関わらずUUIDで検索できる."""
    u = await LUser(email="u1@example.com", display_name="aaa").save()
    res = client.get("/user/search/", params={"id": u.uid})
    assert len(res.json()) == 1

    res = client.get("/user/search/", params={"id": str(UUID(u.uid))})
    assert len(res.json()) == 1


# @mark_async_test()
# async def test_search_username_or_id(client: TestClient):
#     """ユーザーをusername または id で検索できる."""
#     await LUser(uid="a0", email="u1@example.com", username="aaa").save()
#     await LUser(uid="a2", email="u2@example.com", username="bbb").save()
#     await LUser(uid="a3", email="u3@example.com", username="ccc").save()
#     await LUser(uid="a4", email="u4@example.com", username="ddd").save()
#     await LUser(uid="a9", email="u5@example.com", username="eee").save()
#
#     print(await LUser.nodes.all())
#     res = client.get("/user/search/", params={"id": "a"})
#     assert len(res.json()) == 1
#
#     res = client.get("/user/search/", params={"id": "aa"})
#     assert len(res.json()) == 1


@mark_async_test()
async def test_search_username_or_id(client: TestClient):
    """ユーザーをusername または id で検索できる."""
    await LUser(uid="a0", email="u1@example.com", username="aaa").save()
    res = client.get("/user/profile/a")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    res = client.get("/user/profile/aaa")
    assert res.is_success
    u = UserReadPublic.model_validate(res.json())
    assert u.username == "aaa"
