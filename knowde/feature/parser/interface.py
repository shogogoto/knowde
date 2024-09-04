"""interface."""
from typing import IO

import click


@click.command("parse")
@click.argument(
    "stdin",
    type=click.File("r"),
    default="-",
)
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    click.echo(stdin.read())
