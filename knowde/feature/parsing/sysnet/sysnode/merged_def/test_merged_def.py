"""ツリーの重複チェックtest."""

import networkx as nx
import pytest
from pytest_unordered import unordered

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.sysnet.errors import (
    DefSentenceConflictError,
)
from knowde.feature.parsing.sysnet.sysfn import (
    to_def,
)
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.feature.parsing.tree2net.transformer import TSysArg
from knowde.feature.parsing.tree_parser import get_leaves, parse2tree

from . import MergedDef


def test_merged_def() -> None:
    """マージされるtermを持つdefを合体."""
    s = """
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
            Q | qqq
    """
    t = parse2tree(s, TSysArg())
    leaves = get_leaves(t)
    defs = to_def(leaves)
    mdefs, stds, _ = MergedDef.create_and_parted(defs)
    assert mdefs == unordered(
        [
            MergedDef.one(Term.create("A", "A1", "A2"), "aaa1", "aaa2", "aaa3"),
            MergedDef.one(Term.create("B", "B2"), "bbb"),
        ],
    )
    assert stds == unordered(
        [
            Def.create("etc", ["ETC"]),
            Def.dummy_from("C"),
            Def.create("ppp", [], alias="P"),
            Def.create("qqq", [], alias="Q"),
        ],
    )

    # edge追加
    g = nx.MultiDiGraph()
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stds]

    with pytest.raises(DefSentenceConflictError):
        [md.add_edge(g) for md in mdefs]

    with pytest.raises(DefSentenceConflictError):
        [d.add_edge(g) for d in stds]
