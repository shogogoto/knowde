"""ツリーの重複チェックtest."""


import pytest
from pytest_unordered import unordered

from knowde.complex.__core__.tree2net.transformer import TSysArg
from knowde.primitive.parser import parse2tree
from knowde.primitive.term import Term
from knowde.primitive.term.errors import TermConflictError

from . import MergedDef, check_and_merge_term, get_leaves, to_def
from .errors import SentenceConflictError

"""
Tree の段階
    MergedTermグループ
        term1 - stc1
        term2 - stc2
        があるときに
        md - stc1, stc2
        という構造(MergedDef)に変換
            これはsentenceが2つあって取り扱いがおかしくなる
                main -stc を残して、他はbelow関係として扱うか
    add DEF関係(MergedDefも)
    add RESOLVED関係
    QUOTERM置換 先に置換しておける
        replace_node不要説

Interpreter 前に色々やれることはある
    関係追加

"""


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
        check_and_merge_term(leaves)


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
        check_and_merge_term(leaves)


def test_merged_def() -> None:
    """AST."""
    _s = """
        # X
            A: aaa1
            A, A1: aaa2
            A, A2: aaa3
            B: bbb
            B, B2:
                b1
                b2
    """
    _t = parse2tree(_s, TSysArg())
    leaves = get_leaves(_t)
    mt = check_and_merge_term(leaves)
    defs = to_def(leaves)
    assert MergedDef.create(mt, defs) == unordered(
        [
            MergedDef.one(Term.create("A", "A1", "A2"), "aaa1", "aaa2", "aaa3"),
            MergedDef.one(Term.create("B", "B2"), "bbb"),
        ],
    )
