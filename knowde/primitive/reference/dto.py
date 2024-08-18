"""data transfer object."""
from __future__ import annotations

from datetime import date  # noqa: TCH003
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    model_validator,
)
from pydantic_partial.partial import create_partial_model


class BookParam(BaseModel, frozen=True):
    """interface定義用."""

    title: str
    first_edited: date | None = Field(default=None, description="初版発行日")


PartialBookParam = create_partial_model(BookParam)


class SwapParam(BaseModel, frozen=True):
    """interface定義用."""

    order1: int = Field(ge=0)
    order2: int = Field(ge=0)

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.order1 == self.order2:
            msg = "orders must be difference value"
            raise ValueError(msg)
        return self

    @classmethod
    def create(cls, order1: int, order2: int) -> Self:  # noqa: D102
        return cls(
            order1=order1,
            order2=order2,
        )


class HeadlineParam(BaseModel, frozen=True):
    """章節の総称."""

    title: str


class WebParam(BaseModel, frozen=True):
    """Webリソース."""

    title: str
    url: HttpUrl


PartialWebParam = create_partial_model(WebParam)
