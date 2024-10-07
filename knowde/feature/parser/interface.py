"""interface."""
from typing import IO

import click

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.term.visitor import get_termspace


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    tree = transparse(stdin.read())
    s = get_termspace(tree)
    click.echo(s.pretty())
