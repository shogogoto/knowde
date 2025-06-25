"""CLI用手続き."""

from pathlib import Path

import click
import httpx
from fastapi import status

from knowde.feature.auth.repo.client import AuthGet, auth_header
from knowde.feature.entry.namespace.sync import Anchor, filter_parsable
from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings


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


def sync_proc(glob: str, show_error: bool = True) -> None:  # noqa: FBT001 FBT002
    """CLI環境のファイルシステムとDBを同期."""
    c = LocalConfig.load()
    if c.ANCHOR is None:
        click.echo("同期するディレクトリをlinkコマンドで設定してください")
        return
    a = Anchor(c.ANCHOR)
    h = auth_header()  # ユーザーを待たせないためにparse前に失敗したい
    res = AuthGet().me()
    if res.status_code == status.HTTP_401_UNAUTHORIZED:
        click.echo("ログインしてください")
        return
    data = a.to_metas(
        a.rglob(glob),
        filter_parsable(handle_error=print_error if show_error else None),
    )
    s = Settings()
    res = s.post("/namespace", json=data.model_dump(mode="json"), headers=h)
    if not res.is_success:
        print("サーバーエラー")  # noqa: T201
        print(f"'{res.text}'")  # noqa: T201
        return
    op = []
    for _p in res.json():
        p = a / _p
        print(f"'{p}'をアップロード中")  # noqa: T201
        reqfiles = []
        with p.open("rb") as f:
            op.append(f)
            reqfiles.append(("files", (p.name, f, "application/octet-stream")))
            res = httpx.post(s.url("/upload"), headers=h, files=reqfiles, timeout=1000)
        if res.is_success:
            print(f"'{p}'をアップロードしました")  # noqa: T201
        else:
            print(f"'{p}'のアップロードに失敗しました")  # noqa: T201
            print(res.text)  # noqa: T201
