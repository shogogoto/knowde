"""cli root."""
from __future__ import annotations

import click

from knowde.complex.auth.cli import user_cli
from knowde.feature.cli.completion import complete_option
from knowde.feature.cli.help_all import help_all_option
from knowde.feature.fs import link_cmd
from knowde.feature.view import view_cli

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="knowde")
@help_all_option()
@complete_option()
def cli() -> None:
    """Knowde CLI."""


@cli.command("config")
def config_cmd() -> None:
    """設定内容の確認."""
    from knowde.primitive.config import CONFIG_PATH, LocalConfig

    click.echo(CONFIG_PATH)
    c = LocalConfig.load()
    click.echo(c.model_dump_json(indent=2))


cli.add_command(view_cli)
cli.add_command(user_cli)
cli.add_command(link_cmd)


if __name__ == "__main__":
    cli()
