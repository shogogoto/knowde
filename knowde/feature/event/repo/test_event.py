"""test event."""


from knowde._feature.location.repo.repo import add_location_root
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde.feature.event.repo.event import add_event, find_event
from knowde.feature.person.domain.lifedate import SOCIETY_TIMELINE


def test_aaa() -> None:
    """Xxx."""
    t = fetch_time(SOCIETY_TIMELINE, 2000, 1, 1)
    loc = add_location_root("EN")
    ev = add_event("ev1", loc.valid_uid, t.leaf.valid_uid)
    assert ev == find_event(ev.valid_uid)
