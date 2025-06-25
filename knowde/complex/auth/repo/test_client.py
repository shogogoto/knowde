"""test."""

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.complex.auth.routers import auth_router, user_router

from .client import (
    AuthGet,
    AuthPatch,
    AuthPost,
    save_credential,
)


def _api_client() -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(auth_router)
    api.include_router(user_router)
    return TestClient(api)


def test_crud_user() -> None:
    """User CRUD flow."""
    client = _api_client()

    # info = AuthArgs(email="user@example.com", password="password")
    email = f"user-{uuid4()}@example.com"
    password = "password"  # noqa: S105
    p = AuthPost(client=client.post)
    assert not p.login(email, password).is_success
    res = p.register(email, password)
    assert res.is_success
    login_res = p.login(email, password)
    assert login_res.is_success
    save_credential(login_res)

    g = AuthGet(client=client.get)
    res = g.me()
    assert res.is_success

    assert res.json()["email"] == email
    email2 = "user@gmail.com"
    pa = AuthPatch(client=client.patch)
    res = pa.change_me(email2)
    assert res.is_success
    assert res.json()["email"] == email2
