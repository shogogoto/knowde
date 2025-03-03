"""single sign on."""
from __future__ import annotations

import json
import webbrowser
from typing import TYPE_CHECKING, Final
from uuid import UUID

import click
import requests
from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings
from knowde.primitive.user import User

from .manager import auth_backend, get_user_manager

if TYPE_CHECKING:
    from fastapi import APIRouter


def browse_for_sso() -> bool:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = 8000

    url = f"http://localhost:{port}{GOOGLE_URL}/authorize"
    try:
        res = requests.get(url, timeout=3)
    except requests.ConnectionError:
        click.echo(f"認証URL'{url}'への接続に失敗しました")
        return False
    auth_url = res.json().get("authorization_url")
    webbrowser.open(auth_url)
    click.echo(
        '{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNWQ3NWViZi1mZmRlLTQ3OTQtYmFhYy0xY2VjYTc1NzFmYmEiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTczOTk1NzQ4NH0.YoEk4jsjKbHx041JHyweHcYIIDocK0x0K8qwbtbWD4Y","token_type":"bearer"}',
    )
    res_text = input("認証後ブラウザに上記のようなレスポンスを入力してください:")
    c = LocalConfig.load()
    c.CREDENTIALS = json.loads(res_text)
    c.save()
    click.echo("認証情報を保存しました")
    click.echo(c.CREDENTIALS)
    return True


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
