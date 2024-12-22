"""系ネットワーク."""

import pytest

from knowde.complex.system.sysnet.errors import SysNetNotFoundError
from knowde.complex.system.sysnet.sysnode import Def
from knowde.primitive.term import Term

from . import EdgeType, SysNet


def test_setup_term() -> None:
    """用語解決."""
    sn = SysNet(root="sys")
    sn.add(EdgeType.HEAD, sn.root, "h1", "h2")
    sn.add(
        EdgeType.SIBLING,
        "h1",
        Def.create("df", ["A"]),
        Def.create("b{A}b", ["B"]),
        Def.create("ccc", ["C{B}"]),
        Def.create("d{CB}d", ["D"]),
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
    assert sn.get_resolved("ppp") == {}
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
    assert sn.get(t) == t
    with pytest.raises(SysNetNotFoundError):
        sn.get("dummy")
    with pytest.raises(SysNetNotFoundError):
        sn.get(Term.create("dummy"))
