"""test."""

from typing import NoReturn

import pytest

from . import DuplicationChecker


class _MYError(Exception):
    pass


def test_dupchk() -> None:
    """重複チェック."""

    def _err_fn(n: str) -> NoReturn:
        msg = f"{n}は重複"
        raise _MYError(msg)

    chk = DuplicationChecker[str](err_fn=_err_fn)
    chk("a")
    with pytest.raises(_MYError):
        chk("a")
