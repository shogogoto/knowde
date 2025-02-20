"""sysnet repo."""
from __future__ import annotations

from typing import TYPE_CHECKING

from lark import Token

if TYPE_CHECKING:
    from networkx import DiGraph

    from knowde.complex.__core__.sysnet.sysnode import SysNode
    from knowde.primitive.__core__.nxutil.edge_type import EdgeType


"""
CREATE nodes
変数名をそれぞれ付与
EDGE部
変数名同士でつないだ関係のCREATE 文


loop edges
    node 2 query
    新規
        変数名を与える
    登録済み


"""


def node2q(n: SysNode, nvars: dict[SysNode, str]) -> str:
    """nodeからcreate可能な文字列に変換."""
    var = nvars.get(n, None)
    if var is None:
        raise ValueError
    match n:
        case Token():  # heading
            return f"({var}:Head {{val: '{n}'}})"
        case _:
            pass
    return ""


def graph2qlist(g: DiGraph) -> list[str]:
    """グラフからCREATE文のリスト."""
    nvars = {n: f"n{i}" for i, n in enumerate(g.nodes)}
    q_create = [f"CREATE {node2q(n, nvars)}" for n in g.nodes]
    q_rel = []
    for u, v, d in g.edges.data():
        t: EdgeType = d["type"]
        q = f"CREATE ({nvars[u]}) {t.arrow} ({nvars[v]})"
        q_rel.append(q)
    return q_create + q_rel


# def sys2db(user: User, sn: SysNet) -> None:
#     """UserのメモをDBに保存."""
#     for e in sn.g.edges:
#         print(e)
#     # resource情報 分離
#     # heading


# def db2sys(user: User, uid: UUID) -> SysNet:
#     """DBからsysnetを復元."""
