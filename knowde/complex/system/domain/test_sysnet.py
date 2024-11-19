"""系ネットワーク."""


from knowde.complex.system.domain.sysnet import Def, EdgeType, SystemNetwork

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





"""


def test_add_node() -> None:
    """いろいろ."""
    sn = SystemNetwork(root="sys")
    sn.head("sys", "h1")
    sn.add(EdgeType.BELOW, "h1", "aaa")
    sn.add(EdgeType.SIBLING, "aaa", Def.create("df", ["A", "A1"], alias="P1"))
    sn.add(EdgeType.SIBLING, "aaa", "bbb")

    # print("")
    # nx.write_network_text(sn.g)

    # print(sn.nested())
    # print(list(sn.g.successors(sn.root)))
    # print(sn.g.edges)
    # nx.lowest_common_ancestor()
    # print(nx.degree_histogram(sn.g))
    # print(nx.density(sn.g))
    # print(list(nx.non_edges(sn.g)))
    # print(nx.number_of_nodes(sn.g))
    # print(nx.number_of_edges(sn.g))

    # print("#" * 80)
    # G = nx.complete_bipartite_graph(2, 3)
    # nx.write_network_text(G)
    # left, right = nx.bipartite.sets(G)
    # nx.write_network_text(left)
    # nx.write_network_text(right)
    # g = nx.wheel_graph(6)
    # nx.write_network_text(g)
    # pp(nx.to_dict_of_dicts(g))

    # グラフの作成とエッジに属性を追加
    # G = nx.DiGraph()
    # G.add_edge(1, 2, attribute="A")
    # G.add_edge(1, 3, attribute="B")
    # G.add_edge(2, 4, attribute="A")
    # G.add_edge(2, 5, attribute="C")
    # G.add_edge(3, 6, attribute="A")
    # G.add_edge(3, 7, attribute="B")

    # nx.write_network_text(G)
    # predecessors = get_pred_with_attr(G, 4, "attribute", "A")
    # print(predecessors)
