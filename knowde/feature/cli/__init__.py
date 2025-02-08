"""cli root."""
from __future__ import annotations

import click

from knowde.feature.cli.completion import complete_option
from knowde.feature.view import detail_cmd, score_cmd, stat_cmd, time_cmd

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="knowde")
@complete_option()
def cli() -> None:
    """Knowde CLI."""


cli.add_command(score_cmd)
cli.add_command(detail_cmd)
cli.add_command(stat_cmd)
cli.add_command(time_cmd)
# vcli = typer.Typer()
# vcli.command("view")(view_vcmd)


# @vcli.command("version")
# def version_() -> None:
#     typer.echo(f"knowde {__version__}")

if __name__ == "__main__":
    cli()
