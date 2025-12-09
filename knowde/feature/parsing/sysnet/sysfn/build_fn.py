"""systemビルド."""

import networkx as nx

from knowde.feature.parsing.primitive.term.errors import TermResolveError
from knowde.feature.parsing.primitive.term.markresolver import MarkResolver
from knowde.feature.parsing.sysnet.sysnode import Def
from knowde.shared.nxutil.edge_type import EdgeType

from . import get_ifdef, to_sentence


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
