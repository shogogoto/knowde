from pydantic import BaseModel, Field

from knowde.core.domain import Entity

MAX_CHARS = 128


class SentenceParam(BaseModel, frozen=True):
    value: str = Field(max_length=MAX_CHARS)


class Sentence(SentenceParam, Entity, frozen=True):
    pass
