"""test duplicable."""
from knowde.complex.tree2net import parse2net


def test_duplicable() -> None:
    """重複可能な文."""
    _s = r"""
        # h1
            1
                +++ dup1 +++
                +++ dup1 +++
                +++ dup1 +++
            2
    """
    _sn = parse2net(_s)
