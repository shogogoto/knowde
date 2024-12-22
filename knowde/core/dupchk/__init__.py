"""重複チェック."""
from __future__ import annotations

from typing import Callable, Generic, Hashable, NoReturn, TypeVar

from pydantic import BaseModel, PrivateAttr

T = TypeVar("T", bound=Hashable)


class DuplicationChecker(
    BaseModel,
    Generic[T],
    # arbitrary_allow_types=True,
):
    """用語重複チェック."""

    err_fn: Callable[[T], NoReturn]
    _ls: list[T] = PrivateAttr(default_factory=list, init=False)

    def __call__(self, n: T) -> None:
        """チェック."""
        if n in self._ls:
            raise self.err_fn(n)
        self._ls.append(n)
