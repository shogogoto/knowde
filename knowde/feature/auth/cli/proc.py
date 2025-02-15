"""遅延importでCLI補間軽くするための分離."""
from __future__ import annotations

import json
import threading
import webbrowser
from typing import TYPE_CHECKING

import click
import uvicorn
from fastapi import FastAPI

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.sso.route import (
    GoogleSSOResponse,
    response_queue,
    router_google_sso,
)
from knowde.primitive.fs import dir_path

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID


def run_server(port: int) -> None:
    """FastAPIサーバーを実行."""
    app = FastAPI()
    app.include_router(router_google_sso(port))
    uvicorn.run(app, host="localhost", port=port)


def browse_for_sso() -> GoogleSSOResponse:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = Settings().SSO_PROT
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    webbrowser.open(f"http://localhost:{port}/google/login")
    return response_queue().get()


def register_proc(email: str, password: str) -> None:
    """アカウント登録."""
    s = Settings()
    res = s.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    if res.ok:
        click.echo("登録に成功しました")
    else:
        click.echo("登録に失敗しました")
    click.echo(json.dumps(res.json(), indent=2))


def login_proc(email: str, password: str) -> None:
    """ログイン."""
    s = Settings()
    res = s.post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
    )
    p = auth_file()
    if res.ok:
        p.write_text(json.dumps(res.json(), indent=2))
        click.echo(f"'{p}'にトークンを保存しました.")
    else:
        click.echo(f"認証に失敗しました:{res.text}")


def logout_proc() -> None:
    """ログアウト."""
    s = Settings()
    res = s.post(
        "/auth/jwt/logout",
    )
    token = read_saved_token()
    res = s.post(
        "/auth/jwt/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.ok:
        click.echo("ログアウトしました.")
    else:
        click.echo("認証に失敗しました")
    click.echo(res.text)


def read_saved_token() -> str:
    """保存されたトークン."""
    p = auth_file()
    if not p.exists():
        click.echo(f"{p}にトークンが取得されていません")
        click.Abort()
    d = json.loads(p.read_text())
    return d["access_token"]


def change_me_proc(
    email: str | None,
    password: str | None,
) -> None:
    """トークンからユーザーを確認."""
    s = Settings()
    change = {
        k: v for k, v in {"email": email, "password": password}.items() if v is not None
    }

    token = read_saved_token()
    res = s.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=change,
    )
    if res.ok:
        click.echo(f"{list(change.keys())}を変更しました.")
    else:
        click.echo("変更に失敗しました.")
        click.echo(res.text)


def get_me_proc() -> None:
    """ログインしたアカウント情報."""
    token = read_saved_token()
    s = Settings()
    res = s.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.ok:
        click.echo(json.dumps(res.json(), indent=2))
    else:
        click.echo("情報取得に失敗しました.")
        click.echo(res.text)


def get_user_proc(uid: UUID) -> None:
    """ログインしたアカウント情報."""
    token = read_saved_token()
    s = Settings()
    res = s.get(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.ok:
        click.echo(json.dumps(res.json(), indent=2))
    else:
        click.echo("情報取得に失敗しました.")
        click.echo(res.text)


def change_user_proc(
    uid: UUID,
    email: str | None,
    password: str | None,
    activate: bool | None,
    tobe_super: bool | None,
) -> None:
    """スーパーユーザーによるアカウント情報の変更."""
    s = Settings()
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
    res = s.patch(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
        json=change,
    )
    if res.ok:
        click.echo(f"{list(change.keys())}を変更しました.")
    else:
        click.echo("変更に失敗しました.")
        click.echo(res.text)


def delete_user_proc(uid: UUID) -> None:
    """アカウント削除."""
    s = Settings()
    token = read_saved_token()
    res = s.delete(
        f"/users/{uid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.ok:
        click.echo("アカウントを削除しました.")
    else:
        click.echo("削除に失敗しました.")
    click.echo(res.text)


def auth_file() -> Path:
    """認証情報ファイルパス."""
    return dir_path() / "auth.json"
