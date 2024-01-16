from pydantic import BaseModel, Field

from knowde._feature._shared.domain import DomainModel

MAX_CHARS = 2**6


class SentenceParam(BaseModel, frozen=True):
    value: str = Field(max_length=MAX_CHARS)


class Sentence(SentenceParam, DomainModel, frozen=True):
    pass
