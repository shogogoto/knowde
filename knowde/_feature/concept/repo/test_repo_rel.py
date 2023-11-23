from knowde._feature.concept.domain import Concept
from knowde._feature.concept.repo.repo import save_concept
from knowde._feature.concept.repo.repo_rel import find_adjacent, refer


def test_adjacent_create_read() -> None:
    """Test."""
    cfrom = save_concept(Concept(name="from"))
    cto = save_concept(Concept(name="to"))
    assert refer(cfrom.valid_uid, cto.valid_uid)

    adj_from = find_adjacent(cfrom.valid_uid)
    assert len(adj_from.sources) == 0
    assert adj_from.dests[0] == cto

    adj_to = find_adjacent(cto.valid_uid)
    assert adj_to.sources[0] == cfrom
    assert len(adj_to.dests) == 0
