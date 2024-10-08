"""cli root."""
from __future__ import annotations

import click

from knowde.complex import deduct_cli, def_cli, event_cli
from knowde.complex.person.interface import person_cli
from knowde.feature import parse_cmd
from knowde.feature.reference.interface import refdef_cli
from knowde.primitive import prop_cli, ref_cli, tl_cli
from knowde.primitive.location.interface import loc_cli

__version__ = "0.0.0"


@click.group()
def cli() -> None:
    """Knowde CLI."""


@cli.command()
def version() -> None:
    """Show self version."""
    click.echo(f"knowde {__version__}")


ref_cli.add_command(refdef_cli)

cli.add_command(def_cli)
cli.add_command(ref_cli)
cli.add_command(prop_cli)
cli.add_command(deduct_cli)
cli.add_command(tl_cli)
cli.add_command(loc_cli)
cli.add_command(person_cli)
cli.add_command(event_cli)

cli.add_command(parse_cmd)
