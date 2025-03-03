"""CLI用手続き."""


from pathlib import Path

import click

from knowde.primitive.config import LocalConfig


def link_proc() -> None:
    """DBと同期するファイルパスを指定."""
    current = Path.cwd()
    c = LocalConfig.load()
    c.LINK = current
    c.save()
    click.echo(f"'{current}'をDBリンクとして設定しました")


def sync_proc() -> None:
    """ファイルシステムと同期.

    ログイン(認証&user_id特定可能)
    linkの設定 (そのpathの配下とDBPathがリンク)
        jump そこへ
    find 配下から再帰的にファイルパスリストを取得
        user_idからnamespaceを取得してそれとの差分を確認
        current にあってnsにない場合
            upload
        current になくてnsにある場合
            download
    """
