"""common."""

import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from cProfile import Profile

from lark import LarkError

from knowde.feature.parsing.parser.errors import ParserError
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.errors import InterpreterError
from knowde.feature.parsing.tree2net import parse2net
from knowde.primitive.term.errors import TermError
from knowde.shared.nxutil.errors import MultiEdgesError


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


@contextmanager
def elapsed_time(name: str) -> Generator:
    """時間測定."""
    start = time.time()
    yield
    end = time.time()
    print(f"{name}: {end - start:.3f}秒")  # noqa: T201
