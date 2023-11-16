"""neo4j label."""


from datetime import datetime

from neomodel import DateTimeProperty, StringProperty, StructuredNode, UniqueIdProperty
from pytz import timezone
from uuid6 import uuid7

TZ = timezone("Asia/Tokyo")


def jst_now() -> datetime:
    """Jst datetime now."""
    return datetime.now(tz=TZ)


JSTProp = DateTimeProperty(default=jst_now())
IdProp = UniqueIdProperty(defult=uuid7().hex)


class LConcept(StructuredNode):
    """neo4j label."""

    __label__ = "Concept"
    uid = IdProp
    name = StringProperty()
    explain = StringProperty()
    # created = DateTimeProperty(default=datetime.now(tz=TZ))
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now
