"""APIを呼ぶCLIによるUserのCRUD."""


from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.feature.auth.api import auth_router
from knowde.feature.auth.cli.proc import (
    change_me_proc,
    get_me_proc,
    login_proc,
    register_proc,
)


def _api_client() -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(auth_router)
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
    email2 = "user@gmail.com"
    assert res.json()["email"] == email
    res = change_me_proc(email2, patch=client.patch)
    assert res.json()["email"] == email2
