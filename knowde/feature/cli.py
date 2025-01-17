"""cli root."""
from __future__ import annotations

import click
import typer

from knowde.feature.view import detail_cmd, score_cmd, stat_cmd

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="knowde")
def cli() -> None:
    """Knowde CLI."""


# @cli.command()
# def version() -> None:
#     """Show self version."""
#     click.echo(f"knowde {__version__}")


# cli.add_command(def_cli)
# cli.add_command(deduct_cli)
# cli.add_command(tl_cli)
cli.add_command(score_cmd)
cli.add_command(detail_cmd)
cli.add_command(stat_cmd)

vcli = typer.Typer()
# vcli.command("view")(view_vcmd)


# @vcli.command("version")
# def version_() -> None:
#     typer.echo(f"knowde {__version__}")
