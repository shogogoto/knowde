"""test user router."""

import pytest
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.api.middleware.logging.log_config import ContextFilter, text_formatter
from knowde.feature.user.schema import UserRead


@pytest.mark.enable_app_logging
def test_update_user(caplog: pytest.LogCaptureFixture):
    """Patch user test."""
    caplog.set_level("INFO")
    handler = caplog.handler
    handler.addFilter(ContextFilter())
    handler.setFormatter(text_formatter())

    client = TestClient(root_router())

    email = "log@test.com"
    pwd = "password"  # noqa: S105
    res = client.post("/auth/register", json={"email": email, "password": pwd})
    assert res.is_success
    res = client.post("/auth/jwt/login", data={"username": email, "password": pwd})
    assert res.is_success
    auth = {"Authorization": f"Bearer {res.json()['access_token']}"}
    res = client.get("/user/me", headers=auth)
    assert res.is_success

    u = UserRead.model_validate(res.json())
    first_id = u.id
    assert u.email == email
    assert u.display_name is None
    assert u.profile is None
    assert u.avatar_url is None

    res = client.patch(
        "/user/me",
        json={"display_name": "test"},
        headers=auth,
    )
    assert res.is_success
    u = UserRead.model_validate(res.json())
    assert u.display_name == "test"
    assert u.profile is None
    assert u.avatar_url is None
    assert u.id == first_id

    res = client.patch(
        "/user/me",
        json={"username": "ididid"},
        headers=auth,
    )
    assert res.is_success
    u = UserRead.model_validate(res.json())
    assert u.display_name == "test"
    assert u.profile is None
    assert u.avatar_url is None
    assert u.username == "ididid"

    res = client.get("/user/me", headers=auth)
    u = UserRead.model_validate(res.json())
    assert u.display_name == "test"
    assert u.profile is None
    assert u.avatar_url is None
    assert u.username == "ididid"
