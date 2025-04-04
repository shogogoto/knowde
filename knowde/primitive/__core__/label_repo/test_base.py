"""test."""

from .base import LBase


class LTest(LBase):  # noqa: D101
    pass


def test_get_label_name() -> None:  # noqa: D103
    assert LTest.label() == "Test"
