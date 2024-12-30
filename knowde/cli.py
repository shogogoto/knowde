"""cli root."""
from __future__ import annotations

import click

from knowde.complex import deduct_cli, def_cli
from knowde.feature.parser import input_group
from knowde.primitive import tl_cli

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


cli.add_command(def_cli)
cli.add_command(deduct_cli)
cli.add_command(tl_cli)
cli.add_command(input_group)
