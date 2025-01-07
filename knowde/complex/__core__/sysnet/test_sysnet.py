"""系ネットワーク."""

import pytest

from knowde.primitive.term import Term

from . import EdgeType, SysNet
from .errors import SysNetNotFoundError
from .sysnode import Def, Duplicable


def test_resolved() -> None:
    """用語解決."""
    sn = SysNet(root="sys")
    sn.add(EdgeType.HEAD, sn.root, "h1", "h2")
    sn.add(
        EdgeType.SIBLING,
        "h1",
        Def.create("df", ["A"]),  # term, sentence 0 0
        Def.create("b{A}b", ["B"]),  # 0 1
        Def.create("ccc", ["C{B}"]),  # 1 0
        Def.create("d{CB}d", ["D"]),  # 2 0
    )
    sn.add(
        EdgeType.SIBLING,
        "h2",
        Def.create("ppp", ["P{D}"]),
        Def.create("qqq", ["Q"]),
        Term.create("X"),
    )
    sn.add_resolved_edges()
    assert sn.get_resolved("df") == {}
    assert sn.get_resolved("b{A}b") == {"df": {}}
    assert sn.get_resolved("ccc") == {"b{A}b": {"df": {}}}
    assert sn.get_resolved("d{CB}d") == {"ccc": {"b{A}b": {"df": {}}}}
    assert sn.get_resolved("ppp") == {"d{CB}d": {"ccc": {"b{A}b": {"df": {}}}}}
    assert sn.get_resolved("qqq") == {}


def test_get() -> None:
    """文に紐づく用語があれば定義を返す."""
    sn = SysNet(root="sys")
    df = Def.create("aaa", ["A"])
    t = Term.create("B")
    sn.add(EdgeType.BELOW, sn.root, df)
    sn.add(EdgeType.BELOW, sn.root, "bbb")
    sn.add(EdgeType.BELOW, sn.root, t)

    assert sn.get("aaa") == df
    assert sn.get(Term.create("A")) == df
    assert sn.get("bbb") == "bbb"
    assert sn.get(t) == Def.dummy(t)
    with pytest.raises(SysNetNotFoundError):
        sn.get("dummy")
    with pytest.raises(SysNetNotFoundError):
        sn.get(Term.create("dummy"))


def test_vacuous_def() -> None:
    """空定義 複数."""
    sn = SysNet(root="sys")
    t1 = Term.create("A")
    t2 = Term.create("B")

    sn.add(EdgeType.BELOW, sn.root, t1, t2)

    assert sn.get(t1) == Def.dummy(t1)
    assert sn.get(t2) != Def.dummy(t1)
    assert sn.get(t2) == Def.dummy(t2)


def test_duplicable() -> None:
    """重複可能な文."""
    sn = SysNet(root="sys")
    d1 = Duplicable(n="+++ dup1 +++")
    d2 = Duplicable(n="+++ dup1 +++")
    sn.add(EdgeType.BELOW, sn.root, d1)
    sn.add(EdgeType.SIBLING, d1, d2)
    assert sn.sentences == [d1, d2]
