from .label import LConcept, to_model


def test_label2model() -> None:
    name = "l2m"
    lc = LConcept(name=name).save()
    m = to_model(lc)
    assert lc.name == m.name
    assert lc.uid == m.uid.hex
