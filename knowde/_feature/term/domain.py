from pydantic import BaseModel, Field

from knowde.core.domain import Entity

MAX_CHARS = 32


class TermParam(BaseModel, frozen=True):
    value: str = Field(max_length=MAX_CHARS, description="用語名")


class Term(TermParam, Entity, frozen=True):
    pass
