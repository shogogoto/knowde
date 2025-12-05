"""file -> sentnet 変換が責務."""

import time
from collections.abc import Generator
from contextlib import contextmanager
from cProfile import Profile

from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.errors import DomainError


def try_parse2net(s: str) -> SysNet:
    """エラーを握りつぶしたパース."""
    try:
        return parse2net(s)
    except Exception as e:
        raise DomainError(msg=f"[{e.__class__.__name__}] {e!s}") from e


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
