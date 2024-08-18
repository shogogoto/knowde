"""domain."""
from pydantic import BaseModel, Field

from knowde.core.domain import Entity

MAX_CHARS = 32


class TermParam(BaseModel, frozen=True):  # noqa: D101
    value: str = Field(max_length=MAX_CHARS, description="用語名")


class Term(TermParam, Entity, frozen=True):  # noqa: D101
    pass
