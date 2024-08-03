"""test event."""
import pytest
from pytest_unordered import unordered

from knowde._feature._shared.errors.domain import CompleteNotFoundError
from knowde._feature.location.repo.repo import add_location_root
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde.feature.event.repo.event import (
    add_event,
    change_event,
    complete_event,
    find_event,
    list_event,
)
from knowde.feature.person.domain.lifedate import SOCIETY_TIMELINE


def test_add_event() -> None:
    """Add event with location time."""
    assert list_event() == []
    t = fetch_time(SOCIETY_TIMELINE, 2000, 1, 1)
    loc = add_location_root("EN")
    ev = add_event("ev1", loc.valid_uid, t.leaf.valid_uid)
    assert ev == find_event(ev.valid_uid)
    assert list_event() == [ev]

    t2 = fetch_time(SOCIETY_TIMELINE, 2000, 1, 2)
    ev2 = add_event("ev2", loc.valid_uid, t2.leaf.valid_uid)
    assert list_event() == unordered([ev, ev2])


def test_change_text() -> None:
    """記述の変更."""
    ev = add_event("ev")
    ev2 = change_event(ev.valid_uid, "changed")
    assert ev.valid_uid == ev2.valid_uid
    assert ev2.text == "changed"


def test_complete_event() -> None:
    """Eventの補完."""
    with pytest.raises(CompleteNotFoundError):
        complete_event("x")

    ev = add_event("xxx")
    ev2 = complete_event(ev.valid_uid.hex[0])
    assert ev == ev2
