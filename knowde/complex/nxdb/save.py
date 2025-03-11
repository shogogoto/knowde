"""save sysnet."""
from __future__ import annotations

from datetime import date
from itertools import pairwise
from typing import TYPE_CHECKING, Any

import networkx as nx
from lark import Token
from more_itertools import collapse

from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.label import LResource
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.__core__.types import Duplicable
from knowde.primitive.term import Term

from . import LHead, LSentence, LTerm

if TYPE_CHECKING:
    from neomodel import StructuredNode

    from knowde.complex.__core__.sysnet import SysNet
    from knowde.complex.__core__.sysnet.sysnode import KNode


def val2str(val: Any) -> str:  # noqa: ANN401
    """値をcypher用文字列へ."""
    match val:
        case list():
            s = ", ".join([val2str(v) for v in val])
            return f"[{s}]"
        case date():
            return f"date('{val}')"
        case _:
            return f"'{val}'"


def label2propstr(lb: StructuredNode) -> str:
    """Neomodel のラベルからcypher用プロパティ文字列へ."""
    kvs = [f"{k}: {val2str(v)}" for k, v in lb.__properties__.items() if v]
    s = ", ".join(kvs)
    return f"{{ {s} }}"


def resource_props(sn: SysNet) -> str:
    """resource(heading root)の永続化."""
    meta = ResourceMeta.of(sn)
    lb = LResource(**meta.model_dump())
    return label2propstr(lb)


def t2labels(t: type[StructuredNode]) -> str:
    """Convert to query string from neomodel type."""
    return ":".join(t.inherited_labels())


def node2q(n: KNode, nvars: dict[KNode, str]) -> str | list[str] | None:
    """nodeからcreate可能な文字列に変換."""
    var = nvars.get(n, None)
    if var is None:
        raise ValueError
    match n:
        case Token() if n.type == "H1":
            pass
        case Token():  # heading
            return f"CREATE ({var}:{t2labels(LHead)} {{val: '{n}'}})"
        case Term():
            ret = []
            for i, name in enumerate(n.names):
                ivar = f"{var}_{i}" if i > 0 else var
                c = f"CREATE ({ivar}:{t2labels(LTerm)} {{val: '{name}'}})"
                ret.append(c)
            return ret
        case str() | Duplicable():
            return f"CREATE ({var}:{t2labels(LSentence)} {{val: '{n}'}})"
        case _:
            return None
    return None


def reconnect_root_below(sn: SysNet, varnames: dict[KNode, str]) -> str | None:
    """Resource infoを除外したときにbelowが途切れるのを防ぐ."""
    nodes = set(sn.meta)
    vs = set()
    for n in nodes:
        uvs = sn.g.edges(n)
        for uv in uvs:
            vs.add(uv[1])
    belows = list(vs - nodes)
    match len(belows):
        case 0:
            return None
        case 1:
            r = varnames[sn.root]
            b = varnames[belows[0]]
            return f"CREATE ({r}) -[:{EdgeType.BELOW.arrow}]-> ({b})"
        case _:
            raise ValueError


def rel2q(
    edge: tuple[KNode, KNode, dict[str, EdgeType]],
    varnames: dict[KNode, str],
) -> str | list[str] | None:
    """edgeからcreate可能な文字列に変換."""
    u, v, d = edge
    t = d["type"]
    match t:
        case EdgeType.DEF:
            if not isinstance(u, Term):
                raise TypeError
            uv = varnames[u]
            p = f"{{ alias: '{u.alias}' }}" if u.alias else ""
            ret = [f"CREATE ({uv}) -[:{t.arrow} {p}]-> ({varnames[v]})"]
            names = [f"{uv}_{i}" if i > 0 else uv for i, name in enumerate(u.names)]
            ret += [f"CREATE ({x}) -[:TERM]-> ({y})" for x, y in pairwise(names)]
            return ret
        case _:
            return f"CREATE ({varnames[u]}) -[:{t.arrow}]-> ({varnames[v]})"


def sysnet2cypher(sn: SysNet) -> str:
    """sysnetからnodeとrelのcreate文を順次作成."""
    nodes = sn.g.nodes - set(sn.meta)
    varnames = {n: f"n{i}" for i, n in enumerate(nodes)}
    root_var = "root"
    varnames[sn.root] = root_var

    q_root = [f"CREATE ({root_var}:{t2labels(LResource)} {resource_props(sn)})"]
    q_create = q_root + [node2q(n, varnames) for n in nodes]
    g = nx.subgraph_view(
        sn.g,
        filter_node=lambda n: n not in sn.meta,
    )
    q_rel = [rel2q(e, varnames) for e in g.edges.data()]
    q_rel.append(reconnect_root_below(sn, varnames))
    qs = collapse([*q_create, "", *q_rel])
    return "\n".join([q for q in qs if q is not None])
