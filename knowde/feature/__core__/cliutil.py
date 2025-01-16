"""CLI用ユーティリティ."""
from typing import Callable

import click
from click.decorators import FC

from knowde.complex.systats.nw1_n0.syscontext import SysCtxItem


class CLIUtil:
    """cli用param."""

    @classmethod
    def choice(cls) -> click.Choice:
        """Choice."""
        return click.Choice(tuple(SysCtxItem))

    @classmethod
    def item_option(cls) -> Callable[[FC], FC]:
        """表示項目click option."""
        return click.option(
            "-i",
            "--item",
            type=cls.choice(),
            multiple=True,
            default=tuple(SysCtxItem),
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
