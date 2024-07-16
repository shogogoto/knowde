"""event label."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import StringProperty

from knowde._feature._shared.domain.domain import Entity
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.location.repo.label import LLocation
from knowde._feature.timeline.repo.label import LTime
from knowde.feature.event.domain.event import Event

if TYPE_CHECKING:
    from knowde._feature.location.domain import Location
    from knowde._feature.timeline.domain.domain import Time


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
