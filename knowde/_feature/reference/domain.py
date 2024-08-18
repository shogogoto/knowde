from __future__ import annotations

from datetime import date  # noqa: TCH003
from enum import Enum
from textwrap import indent
from typing import Generic, TypeVar

import networkx as nx
from pydantic import BaseModel, Field
from pydantic_core import Url  # noqa: TCH002
from typing_extensions import override

from knowde.core.domain import APIReturn, Entity


class Reference(Entity, frozen=True):
    title: str

    @property
    def output(self) -> str:
        return f"{self.title} ({self.valid_uid})"


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


# Chapterの前に定義しないとUndefinedAnnotationErrorになる
class Section(Reference, frozen=True):
    pass


class Chapter(Reference, frozen=True):
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
    def output(self) -> str:
        s = self.chapter.output
        for i, sec in enumerate(self.sections):
            line = f"{i}. {sec.output}"
            s += "\n" + indent(line, " " * 2)
        return s


class RefType(Enum):
    Book = "book"
    Web = "web"

    @classmethod
    def gettype(cls, r: Reference) -> RefType:
        if isinstance(r, Book):
            return cls.Book
        if isinstance(r, Web):
            return cls.Web
        raise TypeError


class ReferenceTree(APIReturn, Generic[T], frozen=True):
    root: T
    target: Reference
    chapters: list[ChapteredSections] = Field(default_factory=list)
    reftype: RefType

    def get_chapters(self) -> list[Chapter]:
        return [c.chapter for c in self.chapters]

    @property
    def output(self) -> str:
        s = self.output_root
        for i, chap in enumerate(self.chapters):
            line = f"{i}. {chap.output}"
            s += "\n" + indent(line, " " * 2)
        # for chap in self.chapters:
        #     s += "\n" + indent(chap.output, " " * 2)
        #     for sec in chap.sections:
        #         s += "\n" + indent(sec.output, " " * 4)
        return s

    @property
    def output_root(self) -> str:
        if self.reftype == RefType.Book:
            r = Book.model_validate(self.root.model_dump())
            return r.output
        if self.reftype == RefType.Web:
            r = Web.model_validate(self.root.model_dump())
            return r.output
        raise TypeError


class ReferenceGraph(
    BaseModel,
    frozen=True,
    arbitrary_types_allowed=True,
):
    target: Reference
    g: nx.DiGraph

    @property
    def root(self) -> Reference:
        return next(n for n, d in self.g.in_degree() if d == 0)

    def to_tree(self) -> ReferenceTree:
        self.g.add_node(self.target)  # rootが空にならないように
        r = self.root
        attrs = nx.get_edge_attributes(self.g, "order")
        chaps = {}
        for chap in self.g.adj[r]:
            secs = {}
            for sec in self.g.adj[chap]:
                secs[attrs[chap, sec]] = sec
            chaps[attrs[r, chap]] = chap.with_sections(
                [secs[i] for i in sorted(secs.keys())],
            )
        return ReferenceTree(
            root=r,
            target=self.target,
            chapters=[chaps[i] for i in sorted(chaps.keys())],
            reftype=RefType.gettype(r),
        )
