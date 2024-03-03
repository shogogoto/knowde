from __future__ import annotations

from neomodel import DateTimeProperty, StructuredNode, StructuredRel, UniqueIdProperty

from knowde._feature._shared.domain import jst_now


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


class RelBase(StructuredRel, TimestampMixin):
    uid = UniqueIdProperty()
