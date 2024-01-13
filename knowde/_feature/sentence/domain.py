from pydantic import Field

from knowde._feature._shared.domain import DomainModel

MAX_CHARS = 2**6


class Sentence(DomainModel, frozen=True):
    value: str = Field(max_length=MAX_CHARS)
