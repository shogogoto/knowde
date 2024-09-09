"""reference domain model."""
from __future__ import annotations

from textwrap import indent

from knowde.complex.definition.domain.domain import Definition
from knowde.complex.definition.domain.statistics import StatsDefinitions
from knowde.core.domain import APIReturn
from knowde.primitive.reference.domain import Reference


class RefDefinition(APIReturn, frozen=True):
    """引用付き定義."""

    book: Reference
    df: Definition

    @property
    def output(self) -> str:
        """Expression for CLI."""
        return self.book.output + "\n" + indent(self.df.output, " " * 2)


class RefDefinitions(APIReturn, frozen=True):
    """引用付き定義."""

    book: Reference
    defs: StatsDefinitions

    def to_tuple(self) -> tuple[list[Definition], Reference]:
        """To tuple."""
        return (self.defs.defs, self.book)

    @property
    def output(self) -> str:
        """Expression for CLI."""
        s = self.book.output
        for d in self.defs.values:
            s += "\n" + indent(d.output, " " * 2)
        return s
