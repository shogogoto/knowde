"""cli root."""

from __future__ import annotations

import click

from knowde.feature.cli.auth import user_cli
from knowde.feature.cli.fs import anchor_cmd, sync_cmd
from knowde.feature.cli.options.completion import complete_option
from knowde.feature.cli.options.help_all import help_all_option
from knowde.feature.cli.view import view_cli

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
    from knowde.primitive.config import CONFIG_PATH, LocalConfig  # noqa: PLC0415

    click.echo(CONFIG_PATH)
    c = LocalConfig.load()
    click.echo(c.model_dump_json(indent=2))


cli.add_command(view_cli)
cli.add_command(user_cli)
cli.add_command(anchor_cmd)
cli.add_command(sync_cmd)

if __name__ == "__main__":
    cli()
