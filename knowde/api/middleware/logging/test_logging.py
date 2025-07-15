"""test logging."""

import pytest
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.api.middleware.logging.log_config import (
    ContextFilter,
    text_formatter,
)


# テストだとfastapi middlewareが動かずhttpxが動くらしく
# ログを正確に取得できないので、代わりにresponseを確認する
@pytest.mark.enable_app_logging
def test_api_call_logging(caplog: pytest.LogCaptureFixture):
    """ログ確認."""
    caplog.set_level("INFO")
    handler = caplog.handler
    handler.addFilter(ContextFilter())
    # handler.setFormatter(json_formatter())
    handler.setFormatter(text_formatter())
    client = TestClient(root_router())

    res = client.get("/knowde/sentence/064ef00c-5e33-4505-acf5-45ba26cc54dc")
    assert "x-user-id" not in res.headers

    email = "log@test.com"
    pwd = "password"  # noqa: S105
    res = client.post("/auth/register", json={"email": email, "password": pwd})
    assert res.is_success
    assert "x-request-id" in res.headers
    assert "x-url" in res.headers
    assert "x-user-id" not in res.headers

    res = client.post("/auth/jwt/login", data={"username": email, "password": pwd})
    assert res.is_success
    assert "x-request-id" in res.headers
    assert "x-url" in res.headers
    assert "x-user-id" not in res.headers

    auth = {"Authorization": f"Bearer {res.json()['access_token']}"}

    res = client.get("/user/me", headers=auth)
    assert res.is_success
    assert "x-request-id" in res.headers
    assert "x-url" in res.headers
    assert "x-user-id" in res.headers

    # ログイン後はuser-idをレスポンスに付与
    res = client.get(
        "/knowde/sentence/064ef00c-5e33-4505-acf5-45ba26cc54dc",
        headers=auth,
    )
    assert "x-user-id" in res.headers
