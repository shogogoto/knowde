"""CLI用手続き."""


from pathlib import Path

import click

from knowde.complex.auth.repo.client import auth_header
from knowde.complex.entry.repo.sync import path2meta
from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings


def link_proc() -> None:
    """DBと同期するファイルパスを指定."""
    current = Path.cwd()
    c = LocalConfig.load()
    c.ANCHOR = current
    c.save()
    click.echo(f"'{current}'をDBリンクとして設定しました")


class LinkNotExistsError(Exception):
    """リンク設定してない."""


def sync_proc(glob: str, show_error: bool = True) -> None:  # noqa: FBT001 FBT002
    """CLI環境のファイルシステムとDBを同期."""
    c = LocalConfig.load()
    if c.ANCHOR is None:
        click.echo("同期するディレクトリをlinkコマンドで設定してください")
        return
    a = c.ANCHOR
    headers = auth_header()  # ユーザーを待たせないためにparse前に失敗したい
    data = path2meta(a, a.rglob(glob), show_error)
    s = Settings()
    _res = s.post("namespace", json=data.model_dump(mode="json"), headers=headers)
