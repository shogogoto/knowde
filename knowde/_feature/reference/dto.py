from __future__ import annotations

from datetime import date  # noqa: TCH003

from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model


class TitleParam(BaseModel, frozen=True):
    title: str


class BookParam(BaseModel, frozen=True):
    title: str
    first_edited: date


PartialBookParam = create_partial_model(BookParam)


class SwapParam(BaseModel, frozen=True):
    order1: int
    order2: int

    # @model_validator
    # def _validate()


class HeadlineParam(BaseModel, frozen=True):
    """章節の総称."""

    value: str
