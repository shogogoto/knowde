"""cli root."""
from __future__ import annotations

import click

from knowde._feature import concept_cli, ref_cli, s_cli
from knowde.feature import def_cli

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


cli.add_command(concept_cli)
cli.add_command(ref_cli)
cli.add_command(s_cli)
cli.add_command(def_cli)
