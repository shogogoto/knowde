"""系ネットワーク."""


from knowde.complex.system.domain.sysnet import Definition, SysNetwork

"""
headの追加
文の追加

"""


def test_add_heading() -> None:  # noqa: D103
    sn = SysNetwork(root="sys")
    sn.head("sys", "h1")
    sn.head("h1", "h12")
    sn.head("h12", "h121")
    sn.head("h12", "h122")
    sn.head("sys", "h2")
    assert sn.nested() == {
        "h1": {
            "h12": {"h121": {}, "h122": {}},
        },
        "h2": {},
    }
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    # pp(to_nested(sn.g, sn.root, succ_attr("type", EdgeType.HEAD)))


def test_add_node() -> None:
    """いろいろ."""
    sn = SysNetwork(root="sys")
    sn.head("sys", "h1")
    sn.below("h1", "aaa")
    sn.sibling("aaa", Definition.create("df", ["A", "A1"], alias="P1"))
    sn.sibling("aaa", "bbb")

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
