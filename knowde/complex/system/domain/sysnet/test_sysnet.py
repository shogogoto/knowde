"""系ネットワーク."""


from knowde.complex.system.domain.term import Term

from . import (
    EdgeType,
    SystemNetwork,
)
from .sysnode import Def

"""
何ができるようになりたいのか
    永続化したらneo4jに処理を代替させるかも

特定ノードから関連を辿る
    どの見出しの配下か
        見出しパス
    名前解決情報

全文そのまま見るのならテキストで足りてる
    検索
        ヒットした要素の何を返すか
    統計値
        字数
        node数
            文
            用語
            コメント //　無視可能
        edge数
    diff
        nx.differenceで見れそう


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
    sn = SystemNetwork(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    assert sn.headings == {"sys", *{f"h{i}" for i in range(1, 4)}}


def test_setup_term() -> None:
    """用語解決."""
    sn = SystemNetwork(root="sys")
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


# nx.lowest_common_ancestor()
# print(nx.number_of_nodes(sn.g))
# print(nx.number_of_edges(sn.g))
# print(nx.density(sn.g))
