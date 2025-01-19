"""common."""
import sys
from contextlib import contextmanager
from cProfile import Profile
from typing import Generator

from lark import LarkError

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.errors import InterpreterError
from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.__core__.nxutil.errors import MultiEdgesError
from knowde.primitive.parser.errors import ParserError
from knowde.primitive.term.errors import TermError


def try_parse2net(s: str) -> SysNet:
    """エラーを握りつぶしたパース."""
    try:
        return parse2net(s)
    except (
        LarkError,
        ParserError,
        TermError,
        InterpreterError,
        MultiEdgesError,
    ) as e:
        print(f"{type(e).__name__}:", e)  # noqa: T201
    sys.exit(1)


@contextmanager
def profile() -> Generator:
    """パフォーマンス計測してstdout."""
    pr = Profile()
    pr.enable()
    try:
        yield pr
    finally:
        pr.disable()
        pr.print_stats(sort="cumtime")
