"""sysnetの管理.

モチベは?
userId/folder
    CRUD

    root folder user直下
    folder は 配下ではnameが重複してはならない
    rename
    remove 配下のフォルダとsysnetも全て削除
    move parentを差し替える

    folderのCRUD
    folderとCLIのsync upload
        変更があったか否かを低コストでチェックできるとよい
            sysnet のhash値とか使える?

        find コマンドとの連携を考えるか
            自前で作らない方がいい

    folder と CLI userのディレクトリの同期
        CLI find して ファイルパスの構造をそのままsync(永続化)
          -> Git管理できて便利
"""
from __future__ import annotations

import networkx as nx
from pydantic import BaseModel, Field

from knowde.complex.resource.category.folder.errors import FolderNotFoundError
from knowde.complex.resource.category.folder.label import LFolder
from knowde.complex.resource.category.folder.mapper import MFolder  # noqa: TCH001
from knowde.primitive.__core__.types import NXGraph  # noqa: TCH001


class FolderSpace(BaseModel):
    """リソースの分類."""

    g: NXGraph = Field(default_factory=nx.DiGraph)
    roots_: dict[str, MFolder] = Field()

    def children(self, root: str, *names: str) -> list[str]:
        """element_idなしで文字列だけでアクセス."""
        tgt = self.get_or_none(root, *names)
        if tgt is None:
            return []
        return sorted([str(s) for s in self.g.successors(tgt)])

    @property
    def roots(self) -> list[str]:
        """ユーザー直下のフォルダ一覧."""
        return list(self.roots_.keys())

    def get_or_none(self, root: str, *names: str) -> MFolder | None:
        """文字列でパス指定."""
        current = self.roots_.get(root, None)
        if current is None:
            return None
        for name in names:
            succs = [n for n in self.g.successors(current) if str(n) == name]
            if len(succs) != 1:  # 存在しないパスに対して空を返す
                return None
            current = succs[0]
        return current

    def get(self, root: str, *names: str) -> MFolder:
        """Noneの場合にエラー."""
        tgt = self.get_or_none(root, *names)
        if tgt is None:
            raise FolderNotFoundError
        return tgt

    def get_as_label(self, root: str, *names: str) -> LFolder:
        """Neomodel node として取得."""
        tgt = self.get(root, *names)
        return LFolder(**tgt.model_dump())
