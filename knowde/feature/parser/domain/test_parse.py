"""textから章節を抜き出す.

知りたいこと
sourceごと
名前一覧
名前衝突チェック
言明一覧
言明の依存関係情報
文字列への復元
"""

from datetime import date

import pytest
from lark import Tree
from pytest_unordered import unordered

from knowde.feature.parser.domain.errors import NameConflictError
from knowde.feature.parser.domain.knowde import RootTree
from knowde.feature.parser.domain.parser import transparse
from knowde.feature.parser.domain.source import SourceMatchError
from knowde.feature.parser.domain.statement import scan_statements
from knowde.feature.parser.domain.transformer import common_transformer


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


def test_parse_heading() -> None:
    """情報源について."""
    _s = r"""
        # source1
            @author tanaka tarou
            @published 2020-11-11
            xxx
        ## 2.1
            ! multiline
        ### 3.1
            ! define
            xxx
        #### 4.1
        ##### 5.1
        ###### 6.1
        ### 3. dedent
        ### 3. same level
        ### 3. same level
        # source2
        other tree line
            hhh
        !C2
    """
    t = transparse(_s, common_transformer())
    rt = RootTree(tree=t)
    s1 = rt.get_source("source1")
    assert s1.info.tuple == ("source1", "tanaka tarou", date(2020, 11, 11))
    s2 = rt.get_source("source2")
    assert s2.info.tuple == ("source2", None, None)

    with pytest.raises(SourceMatchError):
        rt.get_source("source")

    with pytest.raises(SourceMatchError):
        rt.get_source("xxx")


def test_parse_multiline() -> None:
    """改行ありで一行とみなす."""
    _s = r"""
        # src
            ! multiline
            aaa_\
            bbb
                ccc
                cccc
            ddd
            mul1 \
                mul2 \
                    mul3
    """
    t = transparse(_s, common_transformer())
    _rt = RootTree(tree=t).get_source("src")
    assert scan_statements(_rt.tree) == [
        "aaa_bbb",
        "ccc",
        "cccc",
        "ddd",
        "mul1 mul2 mul3",
    ]


def test_parse_define_and_names() -> None:
    """用語一覧.

    紐づく言明も
    逆に言明に引用された用語の表示
    """
    _s = r"""
        # names
            name1: def1
            name2=name21: def2
            name3 = name31 = name32: def2
            name4: defdef\
                defufu
                child
            def_alias|aname: defdefdefdef
            line_alias|xxx
            c
    """
    t = transparse(_s, common_transformer())
    _rt = RootTree(tree=t).get_source("names")
    _echo(t)
    assert _rt.names == unordered(
        ["name1", "name2", "name21", "name3", "name31", "name32", "name4", "aname"],
    )
    assert _rt.rep_names == unordered(["name1", "name2", "name3", "name4", "aname"])
    assert _rt.aliases == unordered(["def_alias", "line_alias"])


def test_conflict_name() -> None:
    """用語の衝突の検知.

    どことどこの名前が衝突したか
        headingの特定.
    """
    _s = r"""
        # names
            name1: def1
            name1: def1
    """
    t = transparse(_s, common_transformer())
    with pytest.raises(NameConflictError):
        _rt = RootTree(tree=t).get_source("names")


# def test_find_names() -> None:
#     """検索."""


def test_parse_context() -> None:
    """名前一覧."""
    _s = r"""
        # context
            ctx1
                -> b1
                -> b2
                <- c
                <-> d
                e.g. example
                g.e. general
                ref. ref
                1. one
                2. two
    """
    _t = transparse(_s, common_transformer())
    _rt = RootTree(tree=_t)
    _echo(_t)
