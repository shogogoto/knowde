"""系ネットワーク."""


from knowde.complex.system.domain.nxutil import nxprint
from knowde.complex.system.domain.sysnet import (
    Def,
    EdgeType,
    SystemNetwork,
    get_headings,
    heading_path,
)

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

一覧
用語一覧
文一覧

axioms

"""


# pattern
# 直近
# 兄弟
# 文の


def test_get_headings() -> None:
    """見出し一覧."""
    sn = SystemNetwork(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    assert get_headings(sn) == {"sys", *{f"h{i}" for i in range(1, 4)}}


def test_heading_path() -> None:
    """任意のnodeから直近の見出しpathを取得."""
    sn = SystemNetwork(root="sys")
    sn.add(EdgeType.HEAD, *[f"h{i}" for i in range(1, 4)])
    sn.add(EdgeType.SIBLING, "h1", "aaa")
    sn.add(EdgeType.BELOW, "aaa", "Aaa", "AAa")
    sn.add(EdgeType.SIBLING, "h2", "bbb", "ccc")
    sn.add(EdgeType.SIBLING, "x")
    nxprint(sn.g)
    # 隣接
    assert heading_path(sn, "x") == ["sys"]  # root直下
    assert heading_path(sn, "aaa") == ["sys", "h1"]  # 見出しの兄弟
    # 非隣接
    assert heading_path(sn, "Aaa") == ["sys", "h1"]  #   文の下
    assert heading_path(sn, "AAa") == ["sys", "h1"]  #   文の下の下
    assert heading_path(sn, "bbb") == ["sys", "h1", "h2"]
    assert heading_path(sn, "ccc") == ["sys", "h1", "h2"]


def test_add_node() -> None:
    """いろいろ."""
    sn = SystemNetwork(root="sys")
    sn.head("sys", "h1")
    sn.add(EdgeType.BELOW, "h1", "aaa")
    sn.add(EdgeType.SIBLING, "aaa", Def.create("df", ["A", "A1"], alias="P1"))
    sn.add(EdgeType.SIBLING, "aaa", "bbb")
    # nxprint(sn.g)
    # networkx.all_simple_paths()
    # print(sn.nested())
    # print(list(sn.g.successors(sn.root)))
    # print(sn.g.edges)
    # nx.lowest_common_ancestor()
    # print(nx.degree_histogram(sn.g))
    # print(nx.density(sn.g))
    # print(list(nx.non_edges(sn.g)))
    # print(nx.number_of_nodes(sn.g))
    # print(nx.number_of_edges(sn.g))
