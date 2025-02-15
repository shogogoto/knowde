"""auth cli."""
from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from uuid import UUID


@click.group("user")
def user_cli() -> None:
    """ユーザー系."""


@user_cli.command("sso")
def ssologin_cmd() -> None:
    """Login."""
    from .proc import browse_for_sso

    _user = browse_for_sso()


@user_cli.command("register")
@click.argument("email", type=click.STRING)
@click.password_option()
def register_cmd(email: str, password: str) -> None:
    """アカウント作成."""
    from .proc import register_proc

    register_proc(email, password)


@user_cli.command("login")
@click.argument("email", type=click.STRING)
@click.password_option(confirmation_prompt=False)
def login_cmd(email: str, password: str) -> None:
    """ログイン."""
    from .proc import login_proc

    login_proc(email, password)


@user_cli.command("logout")
def logout_cmd() -> None:
    """ログアウト."""
    from .proc import logout_proc

    logout_proc()


@user_cli.command("change-me")
@click.option("--email", type=click.STRING, default=None)
@click.password_option(prompt_required=False, default=None)
def change_me_cmd(
    email: str | None,
    password: str | None,
) -> None:
    """ログインしているアカウント情報の変更."""
    from .proc import change_me_proc

    change_me_proc(email, password)


@user_cli.command("me")
def me_cmd() -> None:
    """ログインしているアカウント情報の取得."""
    from .proc import get_me_proc

    get_me_proc()


@user_cli.command("get")
@click.argument("uid", type=click.UUID)
def get_user_cmd(uid: UUID) -> None:
    """スーパーユーザーによるアカウント情報の取得."""
    from .proc import get_user_proc

    get_user_proc(uid)


@user_cli.command("change")
@click.argument("uid", type=click.UUID)
@click.option("--email", type=click.STRING, default=None)
@click.password_option(prompt_required=False, default=None)
@click.option("--activate", is_flag=True, default=None, type=click.BOOL)
@click.option("--tobe-super", is_flag=True, default=None, type=click.BOOL)
def change_user_cmd(
    uid: UUID,
    email: str | None,
    password: str | None,
    activate: bool | None,
    tobe_super: bool | None,
) -> None:
    """スーパーユーザーによるアカウント情報の変更."""
    from .proc import change_user_proc

    change_user_proc(uid, email, password, activate, tobe_super)


@user_cli.command("delete")
@click.argument("uid", type=click.UUID)
def dekete_user_cmd(uid: UUID) -> None:
    """アカウント削除."""
    from .proc import delete_user_proc

    delete_user_proc(uid)
