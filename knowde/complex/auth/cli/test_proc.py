"""APIを呼ぶCLIによるUserのCRUD."""


from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.complex.auth.routers import auth_router, user_router

from .proc import (
    change_me_proc,
    get_me_proc,
    login_proc,
    register_proc,
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

    email = "user@example.com"
    password = "password"  # noqa: S105

    assert not login_proc(email, password, post=client.post).is_success
    res = register_proc(email, password, post=client.post)
    assert res.is_success
    assert login_proc(email, password, post=client.post).is_success

    res = get_me_proc(client.get)
    assert res.is_success
    assert res.json()["email"] == email
    email2 = "user@gmail.com"
    res = change_me_proc(email2, patch=client.patch)
    assert res.json()["email"] == email2
