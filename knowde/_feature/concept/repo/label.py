"""neo4j label."""
from neomodel import DateTimeProperty, StringProperty, StructuredNode, UniqueIdProperty
from uuid6 import uuid7

from knowde._feature._shared.timeutil import jst_now


class LConcept(StructuredNode):
    """neo4j label."""

    __label__ = "Concept"
    uid = UniqueIdProperty(defult=uuid7().hex)
    name = StringProperty()
    explain = StringProperty()
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now
