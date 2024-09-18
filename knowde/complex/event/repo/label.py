"""event label."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import StringProperty

from knowde.complex.event.domain.event import Event
from knowde.core.domain.domain import Entity
from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.rel import RelUtil
from knowde.core.label_repo.util import LabelUtil
from knowde.primitive.location.repo.label import LLocation
from knowde.primitive.time.repo.label import LTime

if TYPE_CHECKING:
    from knowde.primitive.location.domain import Location
    from knowde.primitive.time.domain.domain import Time


class LEvent(LBase):
    """event label."""

    __label__ = "Event"
    text = StringProperty(required=True)


class EventMapper(Entity, frozen=True):
    """OGM."""

    text: str

    def to_domain(
        self,
        loc: Location | None = None,
        time: Time | None = None,
    ) -> Event:
        """To domain model."""
        return Event(
            uid=self.valid_uid,
            created=self.created,
            updated=self.updated,
            text=self.text,
            when=time,
            where=loc,
        )


EventUtil = LabelUtil(label=LEvent, model=EventMapper)

REL_WHEN = "WHEN"
RelWhen = RelUtil(t_source=LEvent, t_target=LTime, name=REL_WHEN)
REL_WHERE = "WHERE"
RelWhere = RelUtil(t_source=LEvent, t_target=LLocation, name=REL_WHERE)

# REL_WHO = "WHO"
# RelWho = RelUtil(t_source=LEvent, t_target=LPerson, name=REL_WHO)
