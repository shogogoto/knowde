"""CLI用手続き."""

import sys
from collections.abc import Callable
from pathlib import Path

import click
import httpx
from fastapi import status

from knowde.config import LocalConfig
from knowde.config.env import Settings
from knowde.feature.entry.namespace.sync import Anchor, filter_parsable
from knowde.feature.user.routers.repo.client import AuthGet, auth_header


def link_proc() -> None:
    """DBと同期するファイルパスを指定."""
    current = Path.cwd()
    c = LocalConfig.load()
    c.ANCHOR = current
    c.save()
    click.echo(f"'{current}'をDBリンクとして設定しました")


def print_error(p: Path, e: Exception) -> None:
    """エラー処理."""
    print(f"'{p}'のパースに失敗")  # noqa: T201
    print("    ", e)  # noqa: T201


def sync_proc(
    glob: str,
    show_error: bool = True,  # noqa: FBT001, FBT002
    get_client: Callable[..., httpx.Response] = httpx.get,
    post_client: Callable[..., httpx.Response] = httpx.post,
) -> None:
    """CLI環境のファイルシステムとDBを同期."""
    c = LocalConfig.load()
    if c.ANCHOR is None:
        click.echo("同期するディレクトリをlinkコマンドで設定してください")
        sys.exit(1)
    a = Anchor(c.ANCHOR)
    h = auth_header()  # ユーザーを待たせないためにparse前に失敗したい
    res = AuthGet(client=get_client).me()
    if res.status_code == status.HTTP_401_UNAUTHORIZED:
        click.echo(f"ログインしてください: {res.text}")
        sys.exit(1)
    data = a.to_metas(
        a.rglob(glob),
        filter_parsable(handle_error=print_error if show_error else None),
    )
    s = Settings()
    res = s.post(
        "/namespace",
        json=data.model_dump(mode="json"),
        headers=h,
        client=post_client,
    )
    if not res.is_success:
        print("サーバーエラー")  # noqa: T201
        print(f"'{res.text}'")  # noqa: T201
        sys.exit(1)
    op = []
    for _p in res.json():
        p = a / _p
        print(f"'{p}'をアップロード中")  # noqa: T201
        reqfiles = []
        with p.open("rb") as f:
            op.append(f)
            reqfiles.append(("files", (_p, f, "application/octet-stream")))
            res = s.post(
                "/resource",
                headers=h,
                files=reqfiles,
                client=post_client,
            )
        if res.is_success:
            print(f"'{p}'成功")  # noqa: T201
        else:
            print(f"'{p}'失敗")  # noqa: T201
            print(res.text)  # noqa: T201
