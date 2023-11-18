"""cli root."""
from __future__ import annotations

import typer

from .feature.concept import concept_cli

__version__ = "0.0.0"

cli = typer.Typer()
cli.add_typer(concept_cli, name="concept", help="concept CRUD")


@cli.command()
def version() -> None:
    """Show self version."""
    typer.echo(f"knowde {__version__}")
