"""対応するモデルがなくてもneomodel基本操作したい."""
from __future__ import annotations

from typing import Generic, TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.core.errors.domain import NeomodelNotFoundError

L = TypeVar("L", bound=StructuredNode)
M = TypeVar("M", bound=BaseModel)


class NodeUtil(BaseModel, Generic[L], frozen=True):
    """StructuredNodeに対するUtil."""

    t: type[L]

    def find(self, **kwargs) -> L:  # noqa: ANN003
        """TODO:pagingが未実装."""
        return self.t.nodes.filter(**kwargs)

    def find_one(self, **kwargs) -> L:  # noqa: ANN003 D102
        lb = self.find_one_or_none(**kwargs)
        if lb is None:
            raise NeomodelNotFoundError
        return lb

    def find_one_or_none(self, **kwargs) -> L | None:  # noqa: ANN003 D102
        lb = self.t.nodes.get_or_none(**kwargs)
        if lb is None:
            return None
        return lb

    def create(self, **kwargs) -> L:  # noqa: ANN003 D102
        return self.t(**kwargs).save()
