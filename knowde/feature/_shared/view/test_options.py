"""view test."""
from __future__ import annotations

import click
from click.testing import CliRunner

from .options import view_options


@click.command("test")
@view_options
@click.argument("arg", nargs=1)
@click.option("--op", type=click.INT, default=None)
def command(arg: str, op: int | None) -> None:
    click.echo(f"{arg}")
    if op is not None:
        click.echo(op)


def test_wrap() -> None:
    runner = CliRunner()
    result = runner.invoke(
        command,
        ["test", "--op", "111", "-P", "kkk"],
    )
