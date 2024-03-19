from pydantic import BaseModel, Field

from knowde._feature._shared.domain import DomainModel

MAX_CHARS = 32


class TermParam(BaseModel, frozen=True):
    value: str = Field(max_length=MAX_CHARS, description="用語名")


class Term(TermParam, DomainModel, frozen=True):
    pass
