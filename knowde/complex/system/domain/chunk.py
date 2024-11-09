"""系ドメイン."""
from __future__ import annotations

from pydantic import BaseModel

# class Morpheme(BaseModel):
#     """形態素.
#     これ以上分割できない原始的な文字列.
#     e.g. 原子用語, 原子文
#     ただの文字列でいいかも
#     """
#     value: str
# class Word(BaseModel):
#     """語.
#     形態素に分解可能な埋め込みあり文字列
#     """
#     value: str
#     def morphemes(self) -> list[Morpheme]:
#         return []


class Name(BaseModel):
    """埋め込みがない原子用語."""


class Member(BaseModel):
    """Chunkの成員.

    見出しや用語や文や定義
    参照行 ``の行
    """

    term: str | None = None
    sentence: str | None = None


class Chunk(BaseModel):
    """見出しやindentに対応するまとまり.

    文字列表示の単位
    networkへと変換
    """

    members: list[Chunk | Member]

    def to_names(self) -> list[str]:
        """原子用語一覧へ."""
        return []

    # def to_terms(self)
