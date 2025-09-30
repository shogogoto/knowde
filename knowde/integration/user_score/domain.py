"""domain."""

from typing import Self

from pydantic import BaseModel, Field

from knowde.feature.entry.domain import NameSpace
from knowde.shared.user.schema import UserReadPublic


class UserAcheivement(BaseModel, frozen=True):
    """ユーザーの作業量計."""

    n_char: int = Field(title="文字数")
    n_sentence: int = Field(title="単文数")
    n_resource: int = Field(title="リソース数")

    @classmethod
    def from_namspace(cls, ns: NameSpace) -> Self:
        """名前空間のリソース情報から合算."""
        n_char = 0
        n_sentence = 0
        for v in ns.stats.values():
            n_char += v.n_char
            n_sentence += v.n_sentence
        return cls(
            n_char=n_char,
            n_sentence=n_sentence,
            n_resource=len(ns.stats.values()),
        )


class UserSearchRow(BaseModel, frozen=True):
    """検索結果行."""

    user: UserReadPublic
    archivement: UserAcheivement


class UserSearchResult(BaseModel, frozen=True):
    """検索結果."""

    total: int
    data: list[UserSearchRow]
