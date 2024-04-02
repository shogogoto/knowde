from __future__ import annotations

from datetime import date  # noqa: TCH003
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from pydantic_core import Url


class Reference(DomainModel, frozen=True):
    title: str


class Book(Reference, frozen=True):
    """参考文献."""

    first_edited: date | None = Field(title="初版発行日")


class Web(Reference, frozen=True):
    """参考ウェブリソース."""

    url: Url


T = TypeVar("T", bound=Reference)


class ReferenceTree(BaseModel, Generic[T], frozen=True):
    root: T
    chapters: list[Chapter] = Field(default_factory=list)
    title: str


class Headline(DomainModel, frozen=True):
    """章節の総称."""

    value: str


class Chapter(DomainModel, frozen=True):
    value: str
    sections: list[Section] = Field(default_factory=list)


class Section(DomainModel, frozen=True):
    value: str
