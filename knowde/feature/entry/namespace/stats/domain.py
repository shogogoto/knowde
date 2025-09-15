"""domain."""

from collections.abc import Hashable
from functools import cache

import networkx as nx
from pydantic import Field

from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import KNArg
from knowde.shared.nxutil.edge_type import EdgeType, etype_subgraph, is_leaf, is_root


class ResourceStatsStd:
    """基本リソース統計情報."""

    n_char: int = Field(title="文字数")
    n_sentence: int = Field(title="単文数")
    n_term: int = Field(title="単語数")
    n_isoration: int = Field(title="孤立単文数")
    n_axiom = Field(title="公理数")

    def r_isolation(self) -> float:
        """孤立割合. ネットワークのまとまりの悪さ."""
        return self.n_isoration / self.n_sentence

    def r_term(self) -> float:
        """単語割合."""
        return self.n_term / self.n_char


class ResourceStatsHeavy:
    """重いリソース統計情報."""

    n_sentence: int = Field(title="単文数")
    n_term: int = Field(title="単語数")
    n_char: int = Field(title="文字数")


@cache
def get_axiom(sn: SysNet) -> list[Hashable]:
    """TOの出発点となるDef or sentence."""
    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.TO),
        filter_node=lambda n: is_root(sn.g, n, EdgeType.TO),
    )
    return list(sub.nodes)


@cache
def get_unrefered(sn: SysNet) -> list[KNArg]:
    """RESOLVEDの出発点.

    公理に対応する出発点となる用語を無定義用語 undefined term
    これになぞらえた命名
    """
    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.RESOLVED),
        filter_node=lambda n: is_leaf(sn.g, n, EdgeType.RESOLVED),  # 見出し削除
    )
    return list(sub.nodes)
