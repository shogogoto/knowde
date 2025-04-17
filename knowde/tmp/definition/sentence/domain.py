"""domain."""

from pydantic import BaseModel, Field

from knowde.primitive.__core__.domain import Entity

MAX_CHARS = 128


class SentenceParam(BaseModel, frozen=True):  # noqa: D101
    value: str = Field(max_length=MAX_CHARS)


class Sentence(SentenceParam, Entity, frozen=True):  # noqa: D101
    pass
