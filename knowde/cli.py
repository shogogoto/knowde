"""cli root."""
from __future__ import annotations

import click

from knowde.feature.concept.cli import concept_cli

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


cli.add_command(concept_cli)
