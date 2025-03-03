"""cli root."""
from __future__ import annotations

import click

from knowde.feature.auth.cli import user_cli
from knowde.feature.cli.completion import complete_option
from knowde.feature.cli.help_all import help_all_option
from knowde.feature.view import detail_cmd, score_cmd, stat_cmd, time_cmd

__version__ = "0.0.0"


@click.group()
@click.version_option(version=__version__, prog_name="knowde")
@help_all_option()
@complete_option()
def cli() -> None:
    """Knowde CLI."""


@click.command("config")
def config_cmd() -> None:
    """設定の保存パスを出力."""
    from knowde.primitive.config import CONFIG_PATH

    click.echo(CONFIG_PATH)


cli.add_command(score_cmd)
cli.add_command(detail_cmd)
cli.add_command(stat_cmd)
cli.add_command(time_cmd)
cli.add_command(user_cli)

if __name__ == "__main__":
    cli()
