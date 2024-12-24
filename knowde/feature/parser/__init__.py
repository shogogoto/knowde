"""load-file."""

from typing import IO

import click
from lark import LarkError

from knowde.feature.parser.tree2net import parse2net
from knowde.primitive.__core__.nxutil.errors import MultiEdgesError
from knowde.primitive.parser.errors import ParserError
from knowde.primitive.term.errors import MarkUncontainedError


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    txt = stdin.read()
    try:
        _sn = parse2net(txt)
        # pr = nx.pagerank(sn.graph)
        # pr = {sn.get(k): v for k, v in pr.items()}
        # pp(pr)
        # pp(sorted(pr.items(), key=lambda i: i[1]))
    except ParserError as e:
        print(e)  # noqa: T201
    except LarkError as e:
        print(e)  # noqa: T201
    except MultiEdgesError as e:
        print(e)  # noqa: T201
    except MarkUncontainedError as e:
        print(e)  # noqa: T201
