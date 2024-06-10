from __future__ import annotations

from datetime import date  # noqa: TCH003
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from pydantic import BaseModel, Field
from pydantic_core import Url  # noqa: TCH002

from knowde._feature._shared.domain import APIReturn, Entity

if TYPE_CHECKING:
    from knowde._feature._shared.repo.rel_label import RelOrder


class Reference(Entity, frozen=True):
    title: str


class Book(Reference, frozen=True):
    """参考文献."""

    first_edited: date | None = Field(default=None, title="初版発行日")

    @property
    def output(self) -> str:
        r = self
        return f"{r.title}@{r.first_edited}({r.valid_uid})"


class Web(Reference, frozen=True):
    """参考ウェブリソース."""

    url: Url

    @property
    def output(self) -> str:
        r = self
        return f"{r.title}[{r.url}]({r.valid_uid})"


T = TypeVar("T", bound=Reference)


# Chapterの前に定義しないとUndefinedAnnotationErrorになる
class Section(Reference, frozen=True):
    order: int

    @classmethod
    def from_rel(cls, rel: RelOrder) -> Self:
        lb = rel.start_node()
        return cls(
            title=lb.title,
            order=rel.order,
            uid=lb.uid,
            created=lb.created,
            updated=lb.updated,
        )

    @property
    def output(self) -> str:
        return f"{self.title}({self.valid_uid})"


class Chapter(Reference, frozen=True):
    parent: Reference
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
            title=c.title,
            order=rel.order,
            sections=sections,
            uid=c.uid,
            created=c.created,
            updated=c.updated,
        )

    @property
    def output(self) -> str:
        return f"{self.title}({self.valid_uid})"

    @classmethod
    def isinstance(cls, t: type) -> bool:
        return cls == t


class RefType(Enum):
    Book = "book"
    Web = "web"


class ReferenceTree(APIReturn, Generic[T], frozen=True):
    root: T
    chapters: list[Chapter] = Field(default_factory=list)
    reftype: RefType

    @property
    def output(self) -> str:
        s = self.output_root
        for chap in self.chapters:
            s += "\n" + indent(chap.output, " " * 2)
            for sec in chap.sections:
                s += "\n" + indent(sec.output, " " * 4)
        return s

    @property
    def output_root(self) -> str:
        if self.reftype == "book":
            r = Book.model_validate(self.root.model_dump())
            return r.output
        if self.reftype == "web":
            r = Web.model_validate(self.root.model_dump())
            return r.output
        raise TypeError


# def discriminate_rel(rel: RelOrder) -> None:
#     """ReferenceTreeの関係を識別."""
#     e = rel.end_node()

#     if isinstance(e, LBook):
#         Chapter.from_rel(rel)

#     if isinstance(e, Chapter):
#         pass


class ReferenceGraph(BaseModel, frozen=True):
    target: Reference
