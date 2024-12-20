"""系:知識ネットワークの単位."""


from pydantic import BaseModel


class SourceInfo(BaseModel):
    """情報源のメタ情報."""


class Model(BaseModel):
    """体系間の共通する構造.

    読書記録とその整理を分離できる
    sources: 関連付ける系
    """

    # sources: list[System]


class SystemPresenter(BaseModel):
    """体系を永続化や統合度など統計値などに変換."""

    # def __call__(self, sys: System):
    #     pass

    def load(self) -> None:
        """メモリ表現を得る."""
        ...

    def stage(self) -> None:
        """永続化とメモリの中間一時ファイル."""
