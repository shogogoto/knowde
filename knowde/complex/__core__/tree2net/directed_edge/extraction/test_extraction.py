"""ツリーの重複チェックtest."""


import networkx as nx
import pytest
from pytest_unordered import unordered

from knowde.complex.__core__.sysnet.errors import (
    DefSentenceConflictError,
    SentenceConflictError,
)
from knowde.complex.__core__.sysnet.sysfn import check_duplicated_sentence, to_term
from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.complex.__core__.tree2net.transformer import TSysArg
from knowde.primitive.parser import get_leaves, parse2tree
from knowde.primitive.term import Term
from knowde.primitive.term.errors import TermConflictError

from . import MergedDef, check_and_merge_term, to_def


def test_duplicate_term() -> None:
    """用語重複."""
    _s = """
        # X
            A: aaa
            A: dupl
    """
    _t = parse2tree(_s, TSysArg())
    leaves = get_leaves(_t)
    with pytest.raises(TermConflictError):
        check_and_merge_term(to_term(leaves))


def test_duplicate_sentence() -> None:
    """文重複."""
    _s = """
        # X
            aaa
            A: aaa
    """
    _t = parse2tree(_s, TSysArg())
    leaves = get_leaves(_t)
    with pytest.raises(SentenceConflictError):
        check_duplicated_sentence(leaves)


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
    assert stddefs == unordered([Def.create("etc", ["ETC"]), Def.dummy_from("C")])

    # edge追加
    g = nx.MultiDiGraph()
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]

    with pytest.raises(DefSentenceConflictError):
        [md.add_edge(g) for md in mdefs]

    with pytest.raises(DefSentenceConflictError):
        [d.add_edge(g) for d in stddefs]
