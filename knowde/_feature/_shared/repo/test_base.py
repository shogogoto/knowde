from .base import LBase


class LTest(LBase):
    pass


def test_get_label_name() -> None:
    assert LTest.label() == "Test"
