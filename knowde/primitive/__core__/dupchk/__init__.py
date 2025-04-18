"""重複チェック."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import NoReturn, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=Hashable)


class DuplicationChecker[T: Hashable](
    BaseModel,
    # arbitrary_allow_types=True,
):
    """用語重複チェック."""

    err_fn: Callable[[T], NoReturn]
    ls: list[T] = Field(default_factory=list, init=False)

    def __call__(self, n: T) -> None:
        """チェック."""
        if n in self.ls:
            raise self.err_fn(n)
        self.ls.append(n)
