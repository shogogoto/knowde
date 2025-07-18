"""google sso test."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from knowde.api import root_router
from knowde.conftest import mark_async_test
from knowde.feature.user.db import AccountDB
from knowde.feature.user.domain import User

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def client() -> TestClient:
    """Test client."""
    return TestClient(root_router())


@mark_async_test()
async def test_google_callback(
    client: TestClient,
    mocker: MockerFixture,
):
    """Test google callback endpoint."""
    state = "test_state"
    token = {
        "access_token": "access_token",
        "expires_in": 3599,
        "scope": "dummy",
        "token_type": "Bearer",
        "id_tolen": "id_token",
        "expires_at": 1752803612,
    }
    mocker.patch(
        "httpx_oauth.integrations.fastapi.OAuth2AuthorizeCallback.__call__",
        return_value=[token, state],
    )
    mocker.patch("jwt.decode", return_value=None)  # exopire を無視
    account_id = "12345"
    account_email = "test@example.com"
    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            200,
            json={
                "resourceName": f"people/{account_id}",
                "emailAddresses": [
                    {
                        "metadata": {
                            "primary": True,
                            "source": {
                                "type": "ACCOUNT",
                                "id": account_id,
                            },
                            "sourcePrimary": True,
                        },
                        "value": account_email,
                    },
                ],
            },
        ),
    )

    user_repo = AccountDB()
    assert await user_repo.get_by_email(account_email) is None

    res = client.get(f"/google/callback?state={state}&code=test_code")
    assert res.is_success
    created_user = await user_repo.get_by_email(account_email)
    assert isinstance(created_user, User)
    assert created_user.email == account_email
    assert len(created_user.oauth_accounts) == 1
    assert created_user.oauth_accounts[0].account_id == f"people/{account_id}"

    # res = client.get(f"/google/callback?state={state}&code=test_code")
    # print(res.text)
    # raise AssertionError
