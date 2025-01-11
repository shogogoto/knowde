"""systemビルド."""


import networkx as nx

from knowde.complex.__core__.sysnet.errors import QuotermNotFoundError
from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.primitive.__core__.nxutil import replace_node
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.term.markresolver import MarkResolver

from . import get_ifdef, to_quoterm, to_sentence


def replace_quoterms(g: nx.DiGraph, resolver: MarkResolver) -> None:
    """引用用語を1文に置換."""
    for qt in to_quoterm(g.nodes):
        name = qt.replace("`", "")
        term = resolver.lookup.get(name)
        if term is None:
            msg = f"'{name}'は用語として定義されていません"
            raise QuotermNotFoundError(msg)
        s = EdgeType.DEF.get_succ_or_none(g, term)
        if s is None:
            raise TypeError
        replace_node(g, qt, s)


def add_resolved_edges(g: nx.DiGraph, resolver: MarkResolver) -> None:
    """Defの依存関係エッジをsentence同士で張る."""
    for s in to_sentence(g.nodes):
        mt = resolver.sentence2marktree(s)  # sentenceからmark tree
        termtree = resolver.mark2term(mt)  # 文のmark解決
        got = get_ifdef(g, s)
        if isinstance(got, Def):  # term側のmark解決
            d = resolver.term2marktree(got.term)
            t_resolved = resolver.mark2term(d)[got.term]
            termtree.update(t_resolved)
        for t in termtree:
            n = get_ifdef(g, t)
            if isinstance(n, Def):
                EdgeType.RESOLVED.add_edge(g, s, n.sentence)
