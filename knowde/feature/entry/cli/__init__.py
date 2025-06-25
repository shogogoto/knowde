"""sysnetの永続化."""

import click


@click.command("anchor")
def anchor_cmd() -> None:
    """カレントディレクトリをDBと同期するファイルパスとして設定."""
    # いちいちcurrent directoryで同期するのは間違いの元なので
    #   link path を予め設定させる
    from .proc import link_proc  # noqa: PLC0415

    link_proc()


@click.command("sync")
@click.option("-g", "--glob", default="**/*.kn", show_default=True, help="検索パターン")
@click.option(
    "-h",
    "--hide-error",
    is_flag=True,
    default=False,
    help="パースエラーを表示",
)
def sync_cmd(glob: str, hide_error: bool) -> None:  # noqa: FBT001
    """ファイルシステムと同期."""
    from .proc import sync_proc  # noqa: PLC0415

    sync_proc(glob, not hide_error)
