"""用語関連."""


import pytest
from pytest_unordered import unordered

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.term.errors import TermConflictError
from knowde.feature.parser.domain.term.visitor import (
    check_name_conflict,
    get_aliases,
    get_names,
    get_rep_names,
)

"""
用語グループ一覧
用語グループ数
見出しごとの用語数

用語の関連を調べる
    用語の説明に含まれる用語
    用語を利用した言明の検索

用語の参照
"""


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
    t = transparse(_s)
    with pytest.raises(TermConflictError):
        check_name_conflict(get_names(t))


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
    t = transparse(_s)
    # echo_tree(t)
    assert get_names(t) == unordered(
        ["name1", "name2", "name21", "name3", "name31", "name32", "name4", "aname"],
    )
    assert get_rep_names(t) == unordered(["name1", "name2", "name3", "name4", "aname"])
    assert get_aliases(t) == unordered(["def_alias", "line_alias"])


# def test_find_names() -> None:
#     """検索."""
