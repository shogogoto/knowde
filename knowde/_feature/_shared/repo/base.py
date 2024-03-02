from __future__ import annotations

from neomodel import DateTimeProperty, StructuredNode, StructuredRel, UniqueIdProperty

from knowde._feature._shared.domain import jst_now


class TimestampMixin:
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def set_datetime(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now


class LBase(StructuredNode, TimestampMixin):
    __abstract_node__ = True
    uid = UniqueIdProperty()

    def pre_save(self) -> None:
        self.set_datetime()


class RelBase(StructuredRel, TimestampMixin):
    uid = UniqueIdProperty()

    def post_save(self) -> None:
        self.set_datetime()
