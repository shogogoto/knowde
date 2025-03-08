"""sysnetの管理.

モチベは?
userId/folder
    remove 配下のフォルダとsysnetも全て削除

    CLIでfile sys と同期
        変更があったか否かを低コストでチェックできるとよい
            sysnet のhash値とか使える?
        find コマンドとの連携を考えるか 自前で作らない方がいい
        Git管理できて便利
"""
from __future__ import annotations

from datetime import date  # noqa: TCH003

import networkx as nx
from pydantic import BaseModel, Field
from pydantic_core import Url  # noqa: TCH002

from knowde.primitive.__core__.types import NXGraph  # noqa: TCH001

from .errors import EntryNotFoundError


class NameSpace(BaseModel):
    """リソースの分類."""

    g: NXGraph = Field(default_factory=nx.DiGraph)
    roots_: dict[str, Entry] = Field()

    def children(self, root: str, *names: str) -> list[str]:
        """element_idなしで文字列だけでアクセス."""
        tgt = self.get_or_none(root, *names)
        if tgt is None:
            return []
        return sorted([str(s) for s in self.g.successors(tgt)])

    @property
    def roots(self) -> list[str]:
        """ユーザー直下のフォルダ一覧."""
        return sorted(self.roots_.keys())

    def get_or_none(self, root: str, *names: str) -> MFolder | None:
        """文字列でパス指定."""
        current = self.roots_.get(root, None)
        if current is None:
            return None
        for name in names:
            succs = [n for n in self.g.successors(current) if n.name == name]
            if len(succs) != 1:  # 存在しないパスに対して空を返す
                return None
            current = succs[0]
        return current

    def get(self, root: str, *names: str) -> MFolder:
        """Noneの場合にエラー."""
        tgt = self.get_or_none(root, *names)
        if tgt is None:
            raise EntryNotFoundError
        return tgt


class Entry(BaseModel, frozen=True):
    """ResourceとFolderのcomposite."""

    name: str
    element_id_property: str | None = None
    # uid: UUID


class MFolder(Entry, frozen=True):
    """LFolderのgraph用Mapper."""

    def __str__(self) -> str:
        """Prefix / でフォルダであることを明示."""
        return f"/{self.name}"


class MResource(Entry, frozen=True):
    """LResourceのOGM."""

    authors: frozenset[str] | None = None
    published: date | None = None
    urls: frozenset[Url] | None = None

    def __str__(self) -> str:
        """For display."""
        return self.name
