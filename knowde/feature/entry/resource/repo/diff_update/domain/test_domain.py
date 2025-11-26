"""差分更新test."""

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.nxutil.edge_type import EdgeType

from . import (
    create_updatediff,
    diff2sets,
    identify_updatediff_term,
    identify_updatediff_txt,
    sysnet2edges,
)


def test_sentence_diff() -> None:
    """文差分."""
    o1 = "A"
    o2 = "XXX"  # deleted
    o3 = "YYY"  # updated
    old = [o1, o2, o3]
    n1 = "A"  # remain
    n2 = "B"  # added
    n3 = "YYX"  # updated
    new = [n1, n2, n3]
    d, a, up = create_updatediff(old, new, identify_updatediff_txt)
    assert d == {o2}
    assert a == {n2}
    assert up == {o3: n3}


def test_term_diff() -> None:
    """用語差分."""
    o1 = Term.create("A")
    o2 = Term.create("XXX")  # deleted
    o3 = Term.create("YYY")  # updated
    old = [o1, o2, o3]
    n1 = Term.create("A")  # remain
    n2 = Term.create("B")  # added
    n3 = Term.create("YYX")  # updated
    new = [n1, n2, n3]
    d, a, up = create_updatediff(old, new, identify_updatediff_term)
    assert d == {o2}
    assert a == {n2}
    assert up == {o3: n3}


def test_edgediff() -> None:
    """関係の変更."""
    txt1 = """
        # title
            A: aaa
            B: bbb
            C: ccc
            ddd
    """

    txt2 = """
        # title
            A: aaa
                BB: bbb
            C: ccc
            ddd
    """
    sn1 = parse2net(txt1)
    sn2 = parse2net(txt2)
    e1 = sysnet2edges(sn1)
    e2 = sysnet2edges(sn2)
    removed, added = diff2sets(e1, e2)
    assert removed == {
        ("aaa", "bbb", EdgeType.SIBLING),
        ("bbb", "ccc", EdgeType.SIBLING),
    }
    assert added == {
        ("aaa", "bbb", EdgeType.BELOW),
        ("aaa", "ccc", EdgeType.SIBLING),
    }
