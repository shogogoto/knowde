"""reference domain model."""
from __future__ import annotations

from textwrap import indent

from knowde._feature._shared.domain import APIReturn
from knowde._feature.reference.domain import Book  # noqa: TCH001
from knowde.feature.definition.domain.domain import Definition  # noqa: TCH001


class RefDefinitions(APIReturn, frozen=True):
    """引用付き定義."""

    book: Book
    defs: list[Definition]

    def to_tuple(self) -> tuple[list[Definition], Book]:
        """To tuple."""
        return (self.defs, self.book)

    @property
    def output(self) -> str:
        """Expression for CLI."""
        s = self.book.output
        for d in self.defs:
            s += "\n" + indent(d.output, " " * 2)
        return s
