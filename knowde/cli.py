"""cli root."""
from __future__ import annotations

import click

from knowde._feature.reference.interface import ref_cli
from knowde.feature import def_cli
from knowde.reference.interface import refdef_cli

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


ref_cli.add_command(refdef_cli)

cli.add_command(def_cli)
cli.add_command(ref_cli)
