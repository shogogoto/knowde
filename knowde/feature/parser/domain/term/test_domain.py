"""terst term domain."""
from knowde.feature.parser.domain.term.domain import TermGroup


def test_term_group() -> None:
    """String test."""
    tg1 = TermGroup(rep="X", aliases=["x1", "x2"])
    tg2 = TermGroup(rep="Y")
    assert str(tg1) == "X(x1, x2)"
    assert str(tg2) == "Y"
