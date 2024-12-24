"""test."""


import pytest

from knowde.complex.__core__.sysnet.errors import DefSentenceConflictError
from knowde.feature.parser.tree2net import parse2net
from knowde.primitive.__core__.nxutil import EdgeType, to_nested
from knowde.primitive.heading import get_heading_path, get_headings


def test_add_heading() -> None:
    """headingを正しく取得できる."""
    _s = """
        # h1
            aaa
            bbb
                ccc
                eee
        ## h2
            fff
            ggg
                -> ddd
        ### h3
            hhh
                iii
                <- jjj
    """
    sn = parse2net(_s)
    assert get_headings(sn.g, sn.root) == {"# h1", "## h2", "### h3"}
    assert get_heading_path(sn.g, sn.root, "ccc") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "ddd") == ["# h1", "## h2"]
    assert get_heading_path(sn.g, sn.root, "iii") == ["# h1", "## h2", "### h3"]
    assert get_heading_path(sn.g, sn.root, "jjj") == ["# h1", "## h2", "### h3"]


def test_add_ctx() -> None:
    """文脈."""
    _s = """
        # h1
            aaa
                <-> anti aaa\
                        aaa
            B: bbb
            C{B}: ccc
                -> D: d{CB}d
                    vvv
                    www
    """

    sn = parse2net(_s)
    assert list(EdgeType.SIBLING.succ(sn.g, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(sn.g, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(sn.g, "ccc")) == []
    assert list(EdgeType.TO.pred(sn.g, "d{CB}d")) == ["ccc"]
    assert to_nested(sn.g, "d{CB}d", EdgeType.BELOW.succ) == {"vvv": {}}
    assert to_nested(sn.g, "vvv", EdgeType.SIBLING.succ) == {"www": {}}
    # 両方向
    assert list(EdgeType.ANTI.succ(sn.g, "aaa")) == ["anti aaaaaa"]
    assert list(EdgeType.ANTI.pred(sn.g, "anti aaaaaa")) == ["aaa"]


def test_replace_quoterm() -> None:
    """引用用語."""
    _s = """
        # h1
            A: aaa
                aAA
                aBB
            B: bbb
        ## h2
            `A`
                ccc
                ddd
    """

    sn = parse2net(_s)
    assert to_nested(sn.g, "aaa", EdgeType.SIBLING.succ) == {"bbb": {}}
    # belowを1つに統合しようと思ったけどやめた
    assert to_nested(sn.g, "aaa", EdgeType.BELOW.succ) == {
        "aAA": {},
        "ccc": {},
    }


def test_duplicate_def_sentence() -> None:
    """エラー再現(定義文重複、引用用語)."""
    _s = """
        # 科学哲学
          人間と自然を分離させたニュートン力学を批判
            by. フリードリヒ・ヴィルヘルム・シェリング, シェリング: dummy
          ウィラード・ファン・オルマン・クワイン: 論理実証主義を支持しつつ反対
            還元主義の否定
              決定的実験: 競合する２つの理論を決着させる適切な実験
                ピエール・デュエム, デュエム: dummy
        ## 18. フランスの伝統
          フランスは伝統故に論理実証主義と距離を保ってきた
            `デュエム`
              物理理論は１つの説明というより数学的命題の体系
    """
    with pytest.raises(DefSentenceConflictError):
        parse2net(_s)
