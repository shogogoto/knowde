"""用語関連."""


import pytest
from pytest_unordered import unordered

from knowde.feature.parser.domain.errors import TermConflictError
from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.source import get_source

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
        _rt = get_source(t, "names")


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
    _rt = get_source(t, "names")
    # _echo(t)
    assert _rt.names == unordered(
        ["name1", "name2", "name21", "name3", "name31", "name32", "name4", "aname"],
    )
    assert _rt.rep_names == unordered(["name1", "name2", "name3", "name4", "aname"])
    assert _rt.aliases == unordered(["def_alias", "line_alias"])


# def test_find_names() -> None:
#     """検索."""
