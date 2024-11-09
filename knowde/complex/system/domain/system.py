"""体系."""
from __future__ import annotations

from pydantic import BaseModel

from knowde.complex.system.domain.chunk import Chunk


class System(BaseModel):
    """知識ネットワークの単位、体系のインメモリ表現.

    テキストで見る以上の情報を引き出せないのなら意味がない

    検索キーワードと関連するものを抽出
    ネットワークに還元される
        name network
        word network
    """

    chunks: list[Chunk]

    def roots(self) -> None:
        """."""

    def terms(self) -> None:
        """用語一覧."""


class SourceInfo(BaseModel):
    """情報源のメタ情報."""


class Model(BaseModel):
    """体系間の共通する構造.

    読書記録とその整理を分離できる

    sources: 関連付ける系
    """

    sources: list[System]


class SystemPresenter(BaseModel):
    """体系を永続化や統合度など統計値などに変換.

    markdownへ
    .knへ
    統合モデルの評価
    chunkの変換の再帰的適用

    output
        DB
        .stageへ
        stdout

    """

    # def __call__(self, sys: System):
    #     pass

    def load(self) -> None:
        """メモリ表現を得る.

        テキストからparse
        DBから読み取り
        stageから読み取り
        """
        ...

    def stage(self) -> None:
        """永続化とメモリの中間一時ファイル.

        編集による差分を確認したい
        まだ永続化したくないけど保存したい
        auto save
            version管理も
        このローカル運用もできるはず
        """
