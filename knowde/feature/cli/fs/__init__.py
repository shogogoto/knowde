"""sysnetの永続化.

CLI commandとして欲しい機能


userとしてログインの有無で影響される

一端guestで


folder crud
sysnet crud
"""
import click


@click.command("link")
def link_cmd() -> None:
    """カレントディレクトリをDBと同期するファイルパスとして設定."""
    # いちいちcurrent directoryで同期するのは間違いの元なので
    #   link path を予め設定させる
    from .proc import link_proc

    link_proc()


@click.command("sync")
def sync_cmd() -> None:
    """ファイルシステムと同期."""
