"""interface."""
from typing import IO

import click

from knowde.feature.parser.domain.parser.parser import transparse


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    _tree = transparse(stdin.read())
    # s = get_termspace(tree)
    # click.echo(s.pretty())


@click.command("parse2")
@click.argument("stdin", type=click.File("r"), default="-")
def parse2_cmd2(stdin: IO) -> None:
    """Stdin."""
    _tree = transparse(stdin.read())
    # s = get_termspace(tree)
    # click.echo(s.pretty())
