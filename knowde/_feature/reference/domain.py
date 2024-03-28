from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from pydantic_core import Url


class Reference(DomainModel, frozen=True):
    title: str
    capters: list[Capter] = Field(default_factory=list)


class Book(Reference, frozen=True):
    pass


class Web(Reference, frozen=True):
    url: Url


class Capter(DomainModel, frozen=True):
    value: str
    sections: list[Section] = Field(default_factory=list)


class Section(DomainModel, frozen=True):
    value: str
