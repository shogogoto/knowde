"""定義ドメインモデル.

用語(rm(value=v).value

    @field_validator("explain")
    def _valid_explain(cls, v: str) -> str:
        return Sentence(value=v).value

"""
from __future__ import annotations

from pydantic import BaseModel, field_validator

from knowde._feature._shared.domain import DomainModel
from knowde._feature.sentence.domain import Sentence, SentenceParam
from knowde._feature.term.domain import Term, TermParam


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


class Definition(DomainModel, frozen=True):
    """定義モデル."""

    term: Term
    sentence: Sentence

    @property
    def name(self) -> str:
        """term.value alias."""
        return self.term.value

    @property
    def explain(self) -> str:
        """Description sentence alias."""
        return self.sentence.value

    @property
    def oneline(self) -> str:
        """1行のテキスト表現."""
        return f"{self.name}: {self.explain}"
