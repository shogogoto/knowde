"""cli root."""
from __future__ import annotations

import click

from knowde.feature.cli.completion import completion_callback
from knowde.feature.view import detail_cmd, score_cmd, stat_cmd

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="knowde")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    expose_value=False,
    is_eager=True,
    callback=completion_callback,
    flag_value="bash",
    help="CLI補完設定を.bashrcなどに追記する.",
)
def cli() -> None:
    """Knowde CLI."""


cli.add_command(score_cmd)
cli.add_command(detail_cmd)
cli.add_command(stat_cmd)

# vcli = typer.Typer()
# vcli.command("view")(view_vcmd)


# @vcli.command("version")
# def version_() -> None:
#     typer.echo(f"knowde {__version__}")

if __name__ == "__main__":
    cli()
