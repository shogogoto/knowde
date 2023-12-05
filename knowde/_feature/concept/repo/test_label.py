from .label import LConcept, util_concept


def test_label2model() -> None:
    name = "l2m"
    lc = LConcept(name=name).save()
    m = util_concept.to_model(lc)
    assert lc.name == m.name
    assert lc.uid == m.uid.hex
