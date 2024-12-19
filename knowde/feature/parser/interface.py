"""interface."""
from typing import IO

import click


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(_stdin: IO) -> None:
    """Stdin."""
    # _tree = transparse(stdin.read())
    # s = get_termspace(tree)
    # click.echo(s.pretty())


@click.command("parse2")
@click.argument("stdin", type=click.File("r"), default="-")
def parse2_cmd2(_stdin: IO) -> None:
    """Stdin."""
    # _tree = transparse(stdin.read())
    # s = get_termspace(tree)
    # click.echo(s.pretty())
