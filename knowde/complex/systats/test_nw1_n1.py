"""netwok1 node1 getter."""


from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats.nw1_n1 import (
    get_details,
    get_parent_or_none,
    has_dependency,
)


def test_get_detail_parent() -> None:
    """詳細."""
    _s = r"""
        # h1
            aaa
            bbb
                b1
                b2
                    b21
                    b22
        ## h2
            ccc
                c1
                c2
    """
    _sn = parse2net(_s)
    assert get_details(_sn, "aaa") == []
    assert get_details(_sn, "bbb") == [["b1", "b2"]]

    assert get_parent_or_none(_sn, "aaa") is None
    assert get_parent_or_none(_sn, "b2") == "bbb"
    assert get_parent_or_none(_sn, "b21") == "b2"
    assert get_parent_or_none(_sn, "# h1") is None
    assert get_parent_or_none(_sn, "## h2") is None


def test_has_dependency() -> None:
    """意味的な依存を持つ."""
    _s = r"""
        # h1
        ## h2
        ### h3
            aaa
                -> bbb
                <- 000
                <-> ccc
                e.g. ddd
                when. 1919
                where. japan
                ~= eee
                g.e. fff
                by. x-men
            bro
                little
    """
    _sn = parse2net(_s)
    assert has_dependency(_sn, "aaa")
    assert not has_dependency(_sn, "bro")
