from __future__ import annotations

from datetime import datetime

from neomodel import DateTimeProperty, StructuredNode, UniqueIdProperty

from knowde._feature._shared.domain import TZ


def jst_now() -> datetime:
    """Jst datetime now truncated microsecond."""
    return datetime.now(tz=TZ).replace(microsecond=0)


class LBase(StructuredNode):
    __abstract_node__ = True
    uid = UniqueIdProperty()
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now
