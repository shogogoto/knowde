"""load-file."""

from typing import IO

import click
from lark import LarkError

from knowde.complex.__core__.sysnet.errors import (
    InterpreterError,
)
from knowde.feature.parser.tree2net import parse2net
from knowde.feature.parser.tree2net.ranking import get_ranking
from knowde.primitive.__core__.nxutil.errors import MultiEdgesError
from knowde.primitive.parser.errors import ParserError
from knowde.primitive.term.errors import TermError


@click.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """Stdin."""
    txt = stdin.read()
    try:
        _sn = parse2net(txt)
        get_ranking(_sn)
        # pr = nx.pagerank(sn.graph)
        # pr = {sn.get(k): v for k, v in pr.items()}
        # pp(pr)
        # pp(sorted(pr.items(), key=lambda i: i[1]))
    except LarkError as e:
        print(e)  # noqa: T201
    except ParserError as e:
        print(e)  # noqa: T201
    except TermError as e:
        print(e)  # noqa: T201
    except InterpreterError as e:
        print(e)  # noqa: T201
    except MultiEdgesError as e:
        print(e)  # noqa: T201
