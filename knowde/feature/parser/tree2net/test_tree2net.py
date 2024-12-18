"""test."""


from knowde.feature.parser.tree2net import parse2net
from knowde.primitive.heading import get_heading_path


def test_add_heading() -> None:
    """headingを正しく取得できる."""
    _s = """
        # h1
            aaa
            bbb
                ccc
                    -> ddd
                    <- eee
        ## h2
            fff
            ggg
        ### h3
            hhh
                iii
    """
    sn = parse2net(_s)
    assert get_heading_path(sn.g, sn.root, "iii") == ["# h1", "## h2", "### h3"]


def test_setup_term() -> None:
    """用語解決."""
    _s = """
        # h1
            aaa
            B: bbb
            C{B}: ccc
                -> D: d{CB}d
                    vvv
                    www
            ppp
                qqq
                <- rrr
            P:
                xxx
                ! comment
                yyy
                zzz
        ## h2
            lll
                1. 1
                2. 2
                3. 3
    """

    # parse2net(_s)
