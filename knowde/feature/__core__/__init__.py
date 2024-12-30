"""common."""
import sys

from lark import LarkError

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.errors import InterpreterError
from knowde.complex.tree2net import parse2net
from knowde.primitive.__core__.nxutil.errors import MultiEdgesError
from knowde.primitive.parser.errors import ParserError
from knowde.primitive.term.errors import TermError


def try_parse2net(s: str) -> SysNet:
    """エラーを握りつぶしたパース."""
    try:
        return parse2net(s)
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
    sys.exit(1)
    return None
