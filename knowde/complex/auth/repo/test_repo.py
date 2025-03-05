"""test."""


from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.complex.auth.repo import (
    AuthArgs,
    AuthGet,
    AuthPatch,
    AuthPost,
    save_credentials,
)
from knowde.complex.auth.routers import auth_router, user_router


def _api_client() -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(auth_router)
    api.include_router(user_router)
    return TestClient(api)


def test_crud_user() -> None:
    """User CRUD flow."""
    client = _api_client()

    info = AuthArgs(email="user@example.com", password="password")  # noqa: S106
    p = AuthPost(client=client.post)
    assert not p.login(info).is_success
    res = p.register(info)
    assert res.is_success
    login_res = p.login(info)
    assert login_res.is_success
    save_credentials(login_res)

    g = AuthGet(client=client.get)
    res = g.me()
    assert res.is_success

    assert res.json()["email"] == info["email"]
    info2 = AuthArgs(email="user@gmail.com", password="password")  # noqa: S106
    pa = AuthPatch(client=client.patch)
    res = pa.change_me(info2)
    assert res.is_success
    assert res.json()["email"] == info2["email"]
