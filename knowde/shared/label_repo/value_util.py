"""対応するモデルがなくてもneomodel基本操作したい."""

from __future__ import annotations

from typing import TypeVar

from neomodel import StructuredNode
from pydantic import BaseModel

from knowde.shared.errors.domain import NotFoundError

L = TypeVar("L", bound=StructuredNode)
M = TypeVar("M", bound=BaseModel)


class NodeUtil[L](BaseModel, frozen=True):
    """StructuredNodeに対するUtil."""

    t: type[L]

    def find(self, **kwargs) -> L:
        """TODO:pagingが未実装."""
        return self.t.nodes.filter(**kwargs)

    def find_one(self, **kwargs) -> L:  # noqa: D102
        lb = self.find_one_or_none(**kwargs)
        if lb is None:
            raise NotFoundError
        return lb

    def find_one_or_none(self, **kwargs) -> L | None:  # noqa: D102
        lb = self.t.nodes.get_or_none(**kwargs)
        if lb is None:
            return None
        return lb

    def create(self, **kwargs) -> L:  # noqa: D102
        return self.t(**kwargs).save()
