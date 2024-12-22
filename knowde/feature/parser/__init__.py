# ruff: noqa
"""load-file."""


from pprint import pp
from typing import IO

import click
from lark import LarkError
from lark.indenter import DedentError
import networkx as nx

from knowde.core.nxutil import nxprint
from knowde.feature.parser.tree2net import parse2net
from knowde.primitive.parser.errors import ParserError


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    txt = stdin.read()
    try:
        sn = parse2net(txt, True)
        nxprint(sn.graph, True)
        pr = nx.pagerank(sn.graph)
        pr = {sn.get(k): v for k, v in pr.items()}
        pp(pr)
        pp(sorted(pr.items(), key=lambda i: i[1]))
    except ParserError as e:
        print(e)  # noqa: T201
    except LarkError as e:
        print(e)  # noqa: T201
