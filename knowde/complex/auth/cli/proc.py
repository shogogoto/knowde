"""遅延importでCLI補間軽くするための分離."""
from __future__ import annotations

import json
import webbrowser
from typing import TYPE_CHECKING

import click
import requests

from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings

if TYPE_CHECKING:
    from uuid import UUID

    from httpx import Response

    from knowde.primitive.config.env import ReqProtocol

s = Settings()


def register_proc(
    email: str,
    password: str,
    post: ReqProtocol = s.post,
) -> Response:
    """アカウント登録."""
    return post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def login_proc(
    email: str,
    password: str,
    post: ReqProtocol = s.post,
) -> Response:
    """ログイン."""
    res = post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
    )
    if res.is_success:
        c = LocalConfig.load()
        c.CREDENTIALS = res.json()
        c.save()
    return res


def read_saved_token() -> str:
    """保存されたトークン."""
    c = LocalConfig.load()
    if not c.CREDENTIALS:
        click.echo("トークンが取得されていません")
        click.Abort()
    return c.CREDENTIALS["access_token"]


def logout_proc(
    post: ReqProtocol = s.post,
) -> Response:
    """ログアウト."""
    token = read_saved_token()
    return post(
        "/auth/jwt/logout",
        headers={"Authorization": f"Bearer {token}"},
    )


def change_me_proc(
    email: str | None = None,
    password: str | None = None,
    patch: ReqProtocol = s.patch,
) -> Response:
    """トークンからユーザーを確認."""
    change = {
        k: v for k, v in {"email": email, "password": password}.items() if v is not None
    }

    token = read_saved_token()
    return patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=change,
    )


def get_me_proc(
    get: ReqProtocol = s.get,
) -> Response:
    """ログインしたアカウント情報."""
    token = read_saved_token()
    return get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )


def get_user_proc(
    uid: UUID,
    get: ReqProtocol = s.get,
) -> Response:
    """ログインしたアカウント情報."""
    token = read_saved_token()
    return get(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
    )


def delete_user_proc(
    uid: UUID,
    delete: ReqProtocol = s.delete,
) -> Response:
    """アカウント削除."""
    token = read_saved_token()
    return delete(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
    )


def change_user_proc(  # noqa: PLR0913
    uid: UUID,
    email: str | None,
    password: str | None,
    activate: bool | None,
    tobe_super: bool | None,
    patch: ReqProtocol = s.patch,
) -> Response:
    """スーパーユーザーによるアカウント情報の変更."""
    change = {
        k: v
        for k, v in {
            "email": email,
            "password": password,
            "is_active": activate,
            "is_superuser": tobe_super,
        }.items()
        if v is not None
    }

    token = read_saved_token()
    return patch(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
        json=change,
    )


def browse_for_sso() -> bool:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = 8000

    url = f"http://localhost:{port}/google/authorize"
    try:
        res = requests.get(url, timeout=3)
    except requests.ConnectionError:
        click.echo(f"認証URL'{url}'への接続に失敗しました")
        return False
    auth_url = res.json().get("authorization_url")
    webbrowser.open(auth_url)
    click.echo(
        '{"access_token":"eyJh...","token_type":"bearer"}',
    )
    res_text = input("認証後ブラウザに上記のようなレスポンスを入力してください:")
    c = LocalConfig.load()
    c.CREDENTIALS = json.loads(res_text)
    c.save()
    click.echo("認証情報を保存しました")
    click.echo(c.CREDENTIALS)
    return True
