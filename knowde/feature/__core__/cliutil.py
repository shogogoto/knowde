"""CLI用ユーティリティ."""
from __future__ import annotations

import click
from tabulate import tabulate


def echo_table(ls: list[dict]) -> None:
    """Echo by tabulate."""
    click.echo(tabulate(ls, headers="keys"))
