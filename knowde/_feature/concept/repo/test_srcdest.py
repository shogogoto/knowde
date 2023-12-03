from knowde._feature.concept.domain.domain import SaveProp
from knowde._feature.concept.domain.rel import DestinationProp, SourceProp
from knowde._feature.concept.repo.repo import save_concept
from knowde._feature.concept.repo.repo_rel import find_adjacent
from knowde._feature.concept.repo.repo_srcdest import add_destination, add_source


def test_add_source() -> None:
    d1 = save_concept(SaveProp(name="dest"))
    s1 = add_source(d1.valid_uid, SourceProp(name="addsrc1"))
    assert d1.valid_uid == s1.dests[0].valid_uid
    assert s1.name == "addsrc1"

    s2 = save_concept(SaveProp(name="addsrc2"))
    add_source(
        d1.valid_uid,
        SourceProp(source_id=s2.valid_uid, name="changed"),
    )
    d2 = find_adjacent(d1.valid_uid)
    assert s2.valid_uid in {s.valid_uid for s in d2.srcs}
    assert "changed" in {s.name for s in d2.srcs}


def test_add_destination() -> None:
    s1 = save_concept(SaveProp(name="src"))
    d1 = add_destination(s1.valid_uid, DestinationProp(name="adddest1"))
    assert s1.valid_uid == d1.srcs[0].valid_uid
    assert d1.name == "adddest1"

    d2 = save_concept(SaveProp(name="adddest2"))
    add_destination(
        s1.valid_uid,
        DestinationProp(destination_id=d2.valid_uid, name="changed2"),
    )
    s2 = find_adjacent(s1.valid_uid)
    assert d2.valid_uid in {d.valid_uid for d in s2.dests}
    assert "changed2" in {d.name for d in s2.dests}
