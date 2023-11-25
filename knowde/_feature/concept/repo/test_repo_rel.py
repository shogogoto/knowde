from knowde._feature.concept.domain.domain import SaveProp
from knowde._feature.concept.repo.repo import save_concept
from knowde._feature.concept.repo.repo_rel import connect, disconnect, find_adjacent


def test_connect_and_disconnect_concept() -> None:
    """Test."""
    cfrom = save_concept(SaveProp(name="from"))
    cto = save_concept(SaveProp(name="to"))
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
