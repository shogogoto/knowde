from uuid import UUID

from knowde._feature.concept.domain.domain import SaveProp
from knowde._feature.concept.repo.repo import save_concept
from knowde._feature.concept.repo.repo_rel import connect, disconnect, find_adjacent


def test_connect_and_disconnect_concept() -> None:
    """Test."""
    cfrom = save_concept(SaveProp(name="from"))
    cto = save_concept(SaveProp(name="to"))
    print(cfrom)
    print(cto)
    assert connect(cfrom.valid_uid, cto.valid_uid)

    adj_from = find_adjacent(cfrom.valid_uid)
    assert len(adj_from.sources) == 0
    assert adj_from.dests[0] == cto

    adj_to = find_adjacent(cto.valid_uid)
    assert adj_to.sources[0] == cfrom
    assert len(adj_to.dests) == 0

    # fail disconnect test not change
    assert not disconnect(cto.valid_uid, cfrom.valid_uid)
    assert adj_to.sources[0] == cfrom
    assert len(adj_to.dests) == 0

    # success disconnect
    assert disconnect(cfrom.valid_uid, cto.valid_uid)
    adj_from = find_adjacent(cfrom.valid_uid)
    assert len(adj_from.sources) == 0
    assert len(adj_from.dests) == 0
    adj_to = find_adjacent(cto.valid_uid)
    assert len(adj_to.sources) == 0
    assert len(adj_to.dests) == 0


def test_save_with_adjacent() -> None:
    """Test."""
    u1 = UUID("783687a1-3692-44a0-887f-fef0341e32c0")
    save_concept(SaveProp(uid=u1, name="test_create1"))
    c = save_concept(SaveProp(name="test_create2", src_ids=[u1.hex[:5]]))
    adj = find_adjacent(u1)
    assert adj.valid_uid == u1
    assert adj.dests[0].valid_uid == c.valid_uid
