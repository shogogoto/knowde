"""ツリーの重複チェックtest."""


import networkx as nx
import pytest
from pytest_unordered import unordered

from knowde.complex.__core__.sysnet.errors import (
    DefSentenceConflictError,
)
from knowde.complex.__core__.sysnet.sysfn import (
    to_def,
    to_term,
)
from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.complex.__core__.tree2net.transformer import TSysArg
from knowde.primitive.parser import get_leaves, parse2tree
from knowde.primitive.term import Term, check_and_merge_term

from . import MergedDef


def test_merged_def() -> None:
    """マージされるtermを持つdefを合体."""
    _s = """
        # X
            A: aaa1
            A, A1: aaa2
            A, A2: aaa3
            B: bbb
            B, B2:
                b1
                b2
            other
            ETC: etc
            C:
            P | ppp
    """
    _t = parse2tree(_s, TSysArg())
    leaves = get_leaves(_t)
    mt = check_and_merge_term(to_term(leaves))
    defs = to_def(leaves)
    mdefs, stddefs = MergedDef.create(mt, defs)
    assert mdefs == unordered(
        [
            MergedDef.one(Term.create("A", "A1", "A2"), "aaa1", "aaa2", "aaa3"),
            MergedDef.one(Term.create("B", "B2"), "bbb"),
        ],
    )
    assert stddefs == unordered(
        [
            Def.create("etc", ["ETC"]),
            Def.dummy_from("C"),
            Def.create("ppp", [], alias="P"),
        ],
    )

    # edge追加
    g = nx.MultiDiGraph()
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]

    with pytest.raises(DefSentenceConflictError):
        [md.add_edge(g) for md in mdefs]

    with pytest.raises(DefSentenceConflictError):
        [d.add_edge(g) for d in stddefs]
