"""用語Visitor."""
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from lark import Token

from knowde.feature.parser.domain.term.errors import TermConflictError

if TYPE_CHECKING:
    from lark import Tree


def check_name_conflict(names: list[str]) -> None:
    """名前の重複チェック."""
    dups = [(name, c) for name, c in Counter(names).items() if c > 1]
    if len(dups) > 0:
        msg = f"次の名前が重複しています:{dups}"
        raise TermConflictError(msg)


def get_names(t: Tree) -> list[str]:
    """名前一覧."""
    ls = []
    for n in t.find_data("name"):
        ls.extend(n.children)
    return [str(e) for e in ls]


def get_rep_names(t: Tree) -> list[str]:
    """代表名一覧."""
    ls = [d.children[0] for d in t.find_data("name")]
    return [str(e) for e in ls]


def get_aliases(t: Tree) -> list[str]:
    """代表名一覧."""
    vs = t.scan_values(lambda x: isinstance(x, Token) and x.type == "ALIAS")
    return [str(e) for e in vs]
