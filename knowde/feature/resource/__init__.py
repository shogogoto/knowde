"""sysnetの永続化.

CLI commandとして欲しい機能


userとしてログインの有無で影響される

一端guestで


folder crud
sysnet crud



"""
import click


@click.group("resource")
def entry_cli() -> None:
    """データベースやリストに追加された項目."""


@entry_cli.command("add")
def _add() -> None:
    pass
