from __future__ import annotations

from datetime import date  # noqa: TCH003
from enum import Enum
from textwrap import indent
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from pydantic import BaseModel, Field
from pydantic_core import Url  # noqa: TCH002
from typing_extensions import override

from knowde._feature._shared.domain import APIReturn, Entity

if TYPE_CHECKING:
    from knowde._feature._shared.repo.rel_label import RelOrder


class Reference(Entity, frozen=True):
    title: str

    @property
    def output(self) -> str:
        return f"{self.title}({self.valid_uid})"


class Book(Reference, frozen=True):
    """参考文献."""

    first_edited: date | None = Field(default=None, title="初版発行日")

    @property
    @override
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


class OrderedReference(Reference, frozen=True):
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


# Chapterの前に定義しないとUndefinedAnnotationErrorになる
class Section(Reference, frozen=True):
    pass


class Chapter(OrderedReference, frozen=True):
    def with_sections(
        self,
        sections: list[Section],
    ) -> ChapteredSections:
        return ChapteredSections(
            chapter=self,
            sections=sections,
        )


class ChapteredSections(BaseModel, frozen=True):
    chapter: Chapter
    sections: list[Section] = Field(default_factory=list)

    @property
    def title(self) -> str:
        return self.chapter.title

    @property
    def order(self) -> int:
        return self.chapter.order

    @property
    def output(self) -> str:
        s = self.chapter.output
        for sec in self.sections:
            s += "\n" + indent(sec.output, " " * 2)
        return s


class RefType(Enum):
    Book = "book"
    Web = "web"


class ReferenceTree(APIReturn, Generic[T], frozen=True):
    root: T
    chapters: list[ChapteredSections] = Field(default_factory=list)
    reftype: RefType

    @property
    def output(self) -> str:
        s = self.output_root
        for chap in self.chapters:
            s += "\n" + indent(chap.output, " " * 2)
        # for chap in self.chapters:
        #     s += "\n" + indent(chap.output, " " * 2)
        #     for sec in chap.sections:
        #         s += "\n" + indent(sec.output, " " * 4)
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


class ReferenceGraph(BaseModel, frozen=True):
    target: Reference
