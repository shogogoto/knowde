"""usecase."""

from __future__ import annotations

import json
from typing import IO

import click
from tabulate import tabulate

from knowde.feature.parsing.domain import try_parse2net

from . import Nw1N0Label


def stat_proc(
    stdin: IO,
    heavy: bool,  # noqa: FBT001
    table: bool,  # noqa: FBT001
) -> None:
    """統計値."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    labels = Nw1N0Label.standard()
    if heavy:
        labels += Nw1N0Label.heavy()

    stat = Nw1N0Label.to_dict(sn, labels)
    if table:
        click.echo(tabulate([stat], headers="keys"))
    else:
        click.echo(json.dumps(stat, indent=2))
