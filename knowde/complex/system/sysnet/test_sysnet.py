"""系ネットワーク."""


import pytest

from knowde.complex.system.sysnet.errors import SysNetNotFoundError
from knowde.primitive.term import Term

from . import (
    EdgeType,
    SysNet,
)
from .sysnode import Def

"""
何ができるようになりたいのか
    永続化したらneo4jに処理を代替させるかも


特定ノードから関連を辿る
    どの見出しの配下か
        見出しパス
    名前解決情報

情報の得方
    NW1つ, node1つ
        navi
        search
            sysnodeを返す, 数値ではない
    NW1つ, node2つ
    NW1つ
        統計stats
            字数
            node数
                文
                用語
                コメント //　無視可能
            edge数
            axioms
            leaves
            なんかグラフ理論の指標
    NW2つ
        差分diff
            nx.differenceで見れそう
            自己との差分
        結合
            名寄: 別NWの用語同士を同一視する

テキスト
見出し-行-文脈木
    行の分解 -> 定義、用語、文
構文木
    見出し、定義、用語、文、文脈
sysnet[unresolved]
    定義の分解
        見出し、用語、文、コメント、文脈
    -> termnet
        用語解決によるedgeをsysnetに追加
            文 (-> marks) -> terms -> 文 の繰り返し
            DEF or RESOLVE 関係を辿れば用語を介した文関係が分かる
sysnet[resolved]
    DBやstageからも作成可能

axioms 依存するものがない大元のノード
    term axioms
    sentence axioms

"""


def test_get_headings() -> None:
    """見出し一覧."""
    sn = SysNet(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    assert sn.headings == {"sys", *{f"h{i}" for i in range(1, 4)}}


def test_setup_term() -> None:
    """用語解決."""
    sn = SysNet(root="sys")
    sn.add(EdgeType.HEAD, "h1")
    sn.add(EdgeType.HEAD, "h2")
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
    sn.setup_resolver()
    assert sn.get_resolved("df") == {}
    assert sn.get_resolved("b{A}b") == {"df": {}}
    assert sn.get_resolved("ccc") == {"b{A}b": {"df": {}}}
    assert sn.get_resolved("d{CB}d") == {"ccc": {"b{A}b": {"df": {}}}}
    assert sn.get_resolved("ppp") == {}
    assert sn.get_resolved("qqq") == {}


def test_heading_path() -> None:
    """任意のnodeから直近の見出しpathを取得."""
    sn = SysNet(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    sn.add(EdgeType.SIBLING, "h1", "aaa")
    sn.add(EdgeType.BELOW, "aaa", "Aaa", "AAa")
    sn.add(EdgeType.SIBLING, "h2", "bbb", "ccc")
    sn.add(EdgeType.SIBLING, "x")
    # 隣接
    assert sn.heading_path("x") == ["sys"]  # root直下
    assert sn.heading_path("aaa") == ["sys", "h1"]  # 見出しの兄弟
    # 非隣接
    assert sn.heading_path("Aaa") == ["sys", "h1"]  #   文の下
    assert sn.heading_path("AAa") == ["sys", "h1"]  #   文の下の下
    assert sn.heading_path("bbb") == ["sys", "h1", "h2"]
    assert sn.heading_path("ccc") == ["sys", "h1", "h2"]


def test_get() -> None:
    """文に紐づく用語があれば定義を返す."""
    sn = SysNet(root="sys")
    df = Def.create("aaa", ["A"])
    t = Term.create("B")
    sn.add(EdgeType.BELOW, df)
    sn.add(EdgeType.BELOW, "bbb")
    sn.add(EdgeType.BELOW, t)

    assert sn.get("aaa") == df
    assert sn.get(Term.create("A")) == df
    assert sn.get("bbb") == "bbb"
    assert sn.get(t) == t
    with pytest.raises(SysNetNotFoundError):
        sn.get("dummy")
    with pytest.raises(SysNetNotFoundError):
        sn.get(Term.create("dummy"))
