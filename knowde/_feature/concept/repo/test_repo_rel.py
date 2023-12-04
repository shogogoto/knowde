from uuid import UUID

import pytest

from knowde._feature.concept.domain.domain import SaveProp
from knowde._feature.concept.domain.rel import AdjacentConcept
from knowde._feature.concept.error import ConnectionNotFoundError
from knowde._feature.concept.repo.repo import save_concept
from knowde._feature.concept.repo.repo_rel import (
    connect,
    disconnect,
    disconnect_all,
    disconnect_dests,
    disconnect_srcs,
    find_adjacent,
)


def test_connect_and_disconnect_concept() -> None:
    """Test."""
    cfrom = save_concept(SaveProp(name="from"))
    cto = save_concept(SaveProp(name="to"))
    connect(cfrom.valid_uid, cto.valid_uid)

    adj_from = find_adjacent(cfrom.valid_uid)
    assert len(adj_from.srcs) == 0
    assert adj_from.dests[0].valid_uid == cto.valid_uid

    adj_to = find_adjacent(cto.valid_uid)
    assert adj_to.srcs[0].valid_uid == cfrom.valid_uid
    assert len(adj_to.dests) == 0

    with pytest.raises(ConnectionNotFoundError):
        disconnect(cto.valid_uid, cfrom.valid_uid)

    # success disconnect
    disconnect(cfrom.valid_uid, cto.valid_uid)
    adj_from = find_adjacent(cfrom.valid_uid)
    assert len(adj_from.srcs) == 0
    assert len(adj_from.dests) == 0
    adj_to = find_adjacent(cto.valid_uid)
    assert len(adj_to.srcs) == 0
    assert len(adj_to.dests) == 0


def test_save_with_adjacent() -> None:
    """Test."""
    u1 = UUID("783687a1-3692-44a0-887f-fef0341e32c0")
    save_concept(SaveProp(uid=u1, name="test_create1"))
    c = save_concept(SaveProp(name="test_create2", src_ids=[u1.hex[:5]]))
    adj = find_adjacent(u1)
    assert adj.valid_uid == u1
    assert adj.dests[0].valid_uid == c.valid_uid


@pytest.fixture()
def adj() -> AdjacentConcept:
    c = save_concept(SaveProp(name="disconn_all"))
    s1 = save_concept(SaveProp(name="src1"))
    s2 = save_concept(SaveProp(name="src2"))
    d1 = save_concept(SaveProp(name="dest1"))
    d2 = save_concept(SaveProp(name="dest2"))
    d3 = save_concept(SaveProp(name="dest3"))

    connect(s1.valid_uid, c.valid_uid)
    connect(s2.valid_uid, c.valid_uid)
    connect(c.valid_uid, d1.valid_uid)
    connect(c.valid_uid, d2.valid_uid)
    connect(c.valid_uid, d3.valid_uid)
    return find_adjacent(c.valid_uid)


def test_disconnect_all(adj: AdjacentConcept) -> None:
    assert len(adj.srcs) == 2  # noqa: PLR2004
    assert len(adj.dests) == 3  # noqa: PLR2004

    disconnect_all(adj.valid_uid)
    adj = find_adjacent(adj.valid_uid)
    assert len(adj.srcs) == 0
    assert len(adj.dests) == 0


def test_disconnect_srcs_and_dests(adj: AdjacentConcept) -> None:
    assert len(adj.srcs) == 2  # noqa: PLR2004
    assert len(adj.dests) == 3  # noqa: PLR2004

    disconnect_srcs(adj.valid_uid)
    disconnect_dests(adj.valid_uid)
    adj = find_adjacent(adj.valid_uid)
    assert len(adj.srcs) == 0
    assert len(adj.dests) == 0
