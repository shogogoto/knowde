"""systemビルド."""

import networkx as nx

from knowde.feature.parsing.sysnet.errors import QuotermNotFoundError
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.primitive.term.errors import TermResolveError
from knowde.primitive.term.markresolver import MarkResolver
from knowde.shared.nxutil import copy_old_edges
from knowde.shared.nxutil.edge_type import EdgeType

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
        EdgeType.QUOTERM.add_edge(g, qt, s)
        copy_old_edges(g, qt, s, EdgeType.SIBLING)
        # g.remove_node(qt)


def add_resolved_edges(g: nx.DiGraph, resolver: MarkResolver) -> None:
    """Defの依存関係エッジをsentence同士で張る."""
    for s in to_sentence(g.nodes):
        mt = resolver.sentence2marktree(s)  # sentenceからmark tree
        termtree = resolver.mark2term(mt)  # 文のmark解決
        got = get_ifdef(g, s)
        if isinstance(got, Def):  # term側のmark解決
            d = resolver.term2marktree(got.term)
            tmd = resolver.mark2term(d)
            t_resolved = tmd.get(got.term)
            if t_resolved is None:
                msg = "'{got.term}'は用語lookupに含まれていません."
                raise TermResolveError(msg, resolver.lookup.values())
            termtree.update(t_resolved)
        for t in termtree:
            n = get_ifdef(g, t)
            if s == n.sentence:  # 応急処置、何かがおかしい
                continue
            if isinstance(n, Def):
                EdgeType.RESOLVED.add_edge(g, s, n.sentence)
