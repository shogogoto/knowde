"""auth cli."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    import httpx


@click.group("user")
def user_cli() -> None:
    """ユーザー系."""


@user_cli.command("google-sso")
def sso_cmd() -> None:
    """Googleによるシングルサインオン."""
    from knowde.feature.user.oauth.browse import browse_for_sso  # noqa: PLC0415
    from knowde.feature.user.routers.repo.client import AuthGet  # noqa: PLC0415

    if browse_for_sso():
        res = AuthGet().me()
        echo_response(res, "Googleによるアカウント作成とログイン")


@user_cli.command("register")
@click.argument("email", type=click.STRING)
@click.password_option()
@click.option("-n", "--name", type=click.STRING, help="表示名")
def register_cmd(email: str, password: str, name: str) -> None:
    """アカウント作成."""
    from knowde.feature.user.routers.repo.client import AuthPost  # noqa: PLC0415

    res = AuthPost().register(email=email, password=password, display_name=name)
    echo_response(res, "登録")
    login_proc(email, password)


@user_cli.command("login")
@click.argument("email", type=click.STRING)
@click.password_option(confirmation_prompt=False)
def login_cmd(email: str, password: str) -> None:
    """ログイン."""
    login_proc(email, password)


def login_proc(email: str, password: str) -> None:  # noqa: D103
    from knowde.feature.user.routers.repo.client import (  # noqa: PLC0415
        AuthPost,
        save_credential,
    )

    res = AuthPost().login(email, password)
    save_credential(res)
    echo_response(res, "ログイン")


@user_cli.command("logout")
def logout_cmd() -> None:
    """ログアウト."""
    from knowde.feature.user.routers.repo.client import AuthPost  # noqa: PLC0415

    res = AuthPost().logout()
    echo_response(res, "ログアウト")


@user_cli.command("change-me")
@click.option("--email", type=click.STRING, default=None)
@click.password_option(prompt_required=False, default=None)
def change_me_cmd(
    email: str | None,
    password: str | None,
) -> None:
    """ログインしているアカウント情報の変更."""
    from knowde.feature.user.routers.repo.client import AuthPatch  # noqa: PLC0415

    res = AuthPatch().change_me({"email": email, "password": password})
    echo_response(res, "アカウント情報の変更")


@user_cli.command("me")
def me_cmd() -> None:
    """ログインしているアカウント情報の取得."""
    from knowde.feature.user.routers.repo.client import AuthGet  # noqa: PLC0415

    res = AuthGet().me()
    echo_response(res, "ログインアカウント情報の取得")


@user_cli.command("clerk")
def clerk_cmd():
    """Trial."""
    from .proc import clerk  # noqa: PLC0415

    clerk()


# @user_cli.command("get")
# @click.argument("uid", type=click.UUID)
# def get_user_cmd(uid: UUID) -> None:
#     """スーパーユーザーによるアカウント情報の取得."""
#     from knowde.feature.user.routers.repo import AuthGet

#     res = AuthGet().user(uid)
#     echo_response(res, "アカウント情報の取得")


# @user_cli.command("change")
# @click.argument("uid", type=click.UUID)
# @click.option("--email", type=click.STRING, default=None)
# @click.password_option(prompt_required=False, default=None)
# @click.option("--activate", is_flag=True, default=None, type=click.BOOL)
# @click.option("--tobe-super", is_flag=True, default=None, type=click.BOOL)
# def change_user_cmd(
#     uid: UUID,
#     email: str | None,
#     password: str | None,
#     activate: bool | None,
#     tobe_super: bool | None,
# ) -> None:
#     """スーパーユーザーによるアカウント情報の変更."""
#     from .proc import change_user_proc

#     res = change_user_proc(uid, email, password, activate, tobe_super)
#     echo_response(res, "アカウント情報の変更")


# @user_cli.command("delete")
# @click.argument("uid", type=click.UUID)
# def delete_user_cmd(uid: UUID) -> None:
#     """アカウント削除."""
#     from .proc import delete_user_proc

#     res = delete_user_proc(uid)
#     echo_response(res, "アカウントの削除")


def echo_response(res: httpx.Response, what: str) -> None:
    """CLIメッセージ表示."""
    if res.is_success:
        click.echo(f"{what}に成功しました.")
        click.echo(json.dumps(res.json(), indent=2))
    else:
        click.echo(f"{what}に失敗しました.")
        click.echo(res.text)
