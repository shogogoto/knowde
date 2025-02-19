"""single sign on."""
from __future__ import annotations

import json
import webbrowser
from enum import Enum
from typing import TYPE_CHECKING, Final
from uuid import UUID

import click
import httpx
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.cli.proc import auth_file
from knowde.feature.auth.manager import auth_backend, get_user_manager
from knowde.primitive.user import User

if TYPE_CHECKING:
    from fastapi import APIRouter


def browse_for_sso() -> None:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = 8000

    url = f"http://localhost:{port}{GOOGLE_URL}/authorize"
    client = httpx.Client()
    res = client.get(url)
    auth_url = res.json().get("authorization_url")
    webbrowser.open(auth_url)
    click.echo(
        '{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNWQ3NWViZi1mZmRlLTQ3OTQtYmFhYy0xY2VjYTc1NzFmYmEiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTczOTk1NzQ4NH0.YoEk4jsjKbHx041JHyweHcYIIDocK0x0K8qwbtbWD4Y","token_type":"bearer"}',
    )
    res_text = input("認証後ブラウザに上記のようなレスポンスを入力してください:")
    p = auth_file()
    js = json.loads(res_text)
    js = json.dumps(js, indent=2)
    p.write_text(js)
    click.echo(f"{p}を以下で上書きしました")
    click.echo(js)


class Provider(Enum):
    """Single Sign on provider."""

    GOOGLE = "google"


GOOGLE_URL: Final = "/google"


def router_google_oauth() -> APIRouter:
    """For fastapi-users."""
    s = Settings()
    rc = FastAPIUsers[User, UUID](get_user_manager, [auth_backend()])
    return rc.get_oauth_router(
        GoogleOAuth2(s.GOOGLE_CLIENT_ID, s.GOOGLE_CLIENT_SECRET),
        auth_backend(),
        s.KN_AUTH_SECRET,
        # redirect_url="/google/callback",
        # associate_by_email=True,
        # is_verified_by_default=True,
    )
