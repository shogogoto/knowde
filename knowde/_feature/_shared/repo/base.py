from __future__ import annotations

from uuid import UUID

from neomodel import (
    DateTimeProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
)

from knowde._feature._shared.errors.domain import NotExistsAccessError
from knowde._feature._shared.timeutil import jst_now


class LBaseNameError(Exception):
    """LBaseの子クラス名は'L'から始まるべし."""


class TimestampMixin:
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now


class LBase(StructuredNode, TimestampMixin):
    __abstract_node__ = True
    uid = UniqueIdProperty()

    @classmethod
    def label(cls) -> str:
        """neo4j上でのnode label名."""
        # Class propertyにしたかったがpython3.13+で非推奨なのでclassmethod.
        name = cls.__name__
        if name[0] == "L":
            return name[1:]
        msg = f"{name}は'L'から始まる名前にしてください"
        raise LBaseNameError(msg)


class RelBase(StructuredRel, TimestampMixin):
    uid = UniqueIdProperty()

    @property
    def valid_uid(self) -> UUID:
        if self.uid is None:
            raise NotExistsAccessError
        return UUID(self.uid)
