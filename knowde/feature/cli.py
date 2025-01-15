"""cli root."""
from __future__ import annotations

import click
import typer

from knowde.feature.view import view_cmd

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


# cli.add_command(def_cli)
# cli.add_command(deduct_cli)
# cli.add_command(tl_cli)
cli.add_command(view_cmd)

vcli = typer.Typer()
# vcli.command("view")(view_vcmd)


# @vcli.command("version")
# def version_() -> None:
#     typer.echo(f"knowde {__version__}")
