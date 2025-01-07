"""sysnetへの要素追加機能."""


import networkx as nx

from knowde.complex.__core__.sysnet.errors import DefSentenceConflictError
from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.primitive.__core__.nxutil import EdgeType


def add_def(g: nx.DiGraph, d: Def) -> None:
    """定義の追加."""
    terms = list(EdgeType.DEF.pred(g, d.sentence))
    match len(terms):
        case 0:  # 新規登録
            EdgeType.DEF.add_edge(g, d.term, d.sentence)
        case l if l == 1 and d.term == terms[0]:  # 登録済み
            pass
        case _:
            msg = f"'{d}'が他の定義文と重複しています"
            raise DefSentenceConflictError(msg, terms)
