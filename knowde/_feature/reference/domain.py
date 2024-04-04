from __future__ import annotations

from datetime import date  # noqa: TCH003
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from pydantic import Field

from knowde._feature._shared.domain import APIReturn, Entity

if TYPE_CHECKING:
    from pydantic_core import Url

    from knowde._feature._shared.repo.rel_label import RelOrder


class Reference(Entity, frozen=True):
    title: str


class Book(Reference, frozen=True):
    """参考文献."""

    first_edited: date | None = Field(default=None, title="初版発行日")


class Web(Reference, frozen=True):
    """参考ウェブリソース."""

    url: Url


T = TypeVar("T", bound=Reference)


class ReferenceTree(APIReturn, Generic[T], frozen=True):
    root: T
    chapters: list[Chapter] = Field(default_factory=list)


class Headline(Entity, frozen=True):
    """章節の総称."""

    value: str


class Chapter(Entity, frozen=True):
    parent: Reference
    value: str
    order: int
    sections: list[Section] = Field(default_factory=list)

    @classmethod
    def from_rel(
        cls,
        rel: RelOrder,
        sections: list[Section] | None = None,
    ) -> Self:
        if sections is None:
            sections = []
        c = rel.start_node()
        return cls(
            parent=Book.to_model(rel.end_node()),
            value=c.value,
            order=rel.order,
            sections=sections,
            uid=c.uid,
            created=c.created,
            updated=c.updated,
        )


class Section(Entity, frozen=True):
    value: str
    order: int

    @classmethod
    def from_rel(cls, rel: RelOrder) -> Self:
        lb = rel.start_node()
        return cls(
            value=lb.value,
            order=rel.order,
            uid=lb.uid,
            created=lb.created,
            updated=lb.updated,
        )
