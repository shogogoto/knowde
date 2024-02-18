"""定義ドメインモデル.

用語(rm(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return Sentence(value=v).value

"""


from pydantic import BaseModel, field_validator

from knowde._feature._shared.domain import DomainModel
from knowde._feature.sentence.domain import SentenceParam
from knowde._feature.term.domain import TermParam


class DefinitionParam(BaseModel, frozen=True):
    """定義パラメータ."""

    name: str
    explain: str

    @field_validator("name")
    def _valid_name(cls, v: str) -> str:
        return TermParam(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return SentenceParam(value=v).value


class Definition(DefinitionParam, DomainModel, frozen=True):
    """定義モデル."""
