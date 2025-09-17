"""cli root."""

from __future__ import annotations

import click

from knowde.feature.entry.cli import anchor_cmd, sync_cmd

# from knowde.feature.parsing.cli import view_cli
from knowde.feature.user.cli import user_cli

from .options.completion import complete_option
from .options.help_all import help_all_option

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
    from knowde.config import LocalConfig  # noqa: PLC0415
    from knowde.config.env import Settings  # noqa: PLC0415

    s = Settings()
    click.echo(s.config_file)
    c = LocalConfig.load()
    click.echo(c.model_dump_json(indent=2))


# cli.add_command(view_cli)
cli.add_command(user_cli)
cli.add_command(anchor_cmd)
cli.add_command(sync_cmd)

if __name__ == "__main__":
    cli()
