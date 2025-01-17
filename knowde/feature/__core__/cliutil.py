"""CLI用ユーティリティ."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import click
from tabulate import tabulate

from knowde.complex.systats.nw1_n0.syscontext import Nw1N1Label

if TYPE_CHECKING:
    from click.decorators import FC


class CLIUtil:
    """cli用param."""

    @classmethod
    def choice(cls) -> click.Choice:
        """Choice."""
        return click.Choice(tuple(Nw1N1Label))

    @classmethod
    def item_option(cls) -> Callable[[FC], FC]:
        """表示項目click option."""
        return click.option(
            "-i",
            "--item",
            type=cls.choice(),
            multiple=True,
            default=tuple(Nw1N1Label),
            show_default=True,
            help="表示項目",
        )

    @classmethod
    def ignore_option(cls) -> Callable[[FC], FC]:
        """非表示項目. click option."""
        return click.option(
            "-ig",
            "--ignore",
            type=cls.choice(),
            multiple=True,
            help="非表示項目",
            show_default=True,
        )


def echo_table(ls: list[dict]) -> None:
    """Echo by tabulate."""
    click.echo(tabulate(ls, headers="keys"))
