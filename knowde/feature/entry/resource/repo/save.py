"""save sysnet."""

from __future__ import annotations

from datetime import date
from itertools import pairwise
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import networkx as nx
from lark import Token
from more_itertools import collapse
from neomodel import StructuredNode, db
from pydantic import BaseModel

from knowde.feature.entry.label import LHead, LResource
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.primitive.time import WhenNode
from knowde.shared.knowde.label import LInterval, LSentence, LTerm
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import Duplicable, to_uuid

if TYPE_CHECKING:
    from knowde.feature.parsing.sysnet import SysNet
    from knowde.feature.parsing.sysnet.sysnode import KNode
    from knowde.shared.types import UUIDy


def val2str(val: Any) -> str:
    """値をcypher用文字列へ."""
    match val:
        case list():
            s = ", ".join([val2str(v) for v in val])
            return f"[{s}]"
        case date():
            return f"date('{val}')"
        case float() | int():
            return str(val)
        case UUID():
            return val.hex
        case _:
            return f"'{val}'"


def propstr(tgt: StructuredNode | BaseModel | dict) -> str:
    """Neomodel のラベルからcypher用プロパティ文字列へ."""
    d = tgt
    if isinstance(tgt, StructuredNode):
        d = tgt.__properties__
    if isinstance(tgt, BaseModel):
        d = tgt.model_dump(mode="json")

    kvs = [f"{k}: {val2str(v)}" for k, v in d.items() if v]
    s = ", ".join(kvs)
    return f"{{ {s} }}"


def t2labels(t: type[StructuredNode]) -> str:
    """Convert to query string from neomodel type."""
    return ":".join(t.inherited_labels())


def q_create_node(
    n: KNode,
    nvars: dict[KNode, str],
) -> str | list[str] | None:
    """nodeからcreate可能な文字列に変換."""
    var = nvars.get(n)
    if var is None:
        raise ValueError
    match n:
        case Token() if n.type == "H1":
            pass
        case Token():  # heading
            uid = getattr(n, "uid", uuid4()).hex
            return f"CREATE ({var}:{t2labels(LHead)} {{val: '{n}', uid: '{uid}'}})"
        case Term():
            ret = []
            for i, name in enumerate(n.names):
                ivar = f"{var}_{i}" if i > 0 else var
                c = f"CREATE ({ivar}:{t2labels(LTerm)} {{val: '{name}'}})"
                ret.append(c)
            return ret
        case WhenNode():
            d = n.model_dump(mode="json")
            d["val"] = d.pop("n")
            return f"CREATE ({var}:{t2labels(LInterval)} {propstr(d)})"
        case str() | Duplicable():
            uid = getattr(n, "uid", uuid4()).hex
            return f"CREATE ({var}:{t2labels(LSentence)} {{val: '{n}', uid: '{uid}', resource_uid: $uid}})"  # noqa: E501
        case _:
            return None
    return None


def reconnect_root_below(sn: SysNet, varnames: dict[KNode, str]) -> str | None:
    """Resource infoを除外したときにbelowが途切れるのを防ぐ."""
    nodes = set(sn.meta)
    vs = set()
    for n in nodes:
        uvs = sn.g.edges(n)
        vs.update(uv[1] for uv in uvs)
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
            ret = [f"CREATE ({uv}) -[:{t.arrow} {p}]-> ({varnames[v]})"]  # DEF
            names = [f"{uv}_{i}" if i > 0 else uv for i, name in enumerate(u.names)]
            # 別名は :ALIAS 関係 term同士の関係
            ret += [f"CREATE ({x}) -[:ALIAS]-> ({y})" for x, y in pairwise(names)]
            return ret
        case _:
            return f"CREATE ({varnames[u]}) -[:{t.arrow}]-> ({varnames[v]})"


def sysnet2cypher(sn: SysNet) -> str:
    """sysnetからnodeとrelのcreate文を順次作成."""
    nodes = sn.g.nodes - set(sn.meta)
    varnames = {n: f"n{i}" for i, n in enumerate(nodes)}
    root_var = "root"
    varnames[sn.root] = root_var
    q_root = [f"MATCH ({root_var}:{t2labels(LResource)} {{uid: $uid}})"]
    q_create = q_root + [q_create_node(n, varnames) for n in nodes]
    g = nx.subgraph_view(
        sn.g,
        filter_node=lambda n: n not in sn.meta,
    )
    q_rel = [rel2q(e, varnames) for e in g.edges.data()]
    q_rel.append(reconnect_root_below(sn, varnames))
    qs = collapse([*q_create, *q_rel])
    return "\n".join([q for q in qs if q is not None])


def sn2db(sn: SysNet, resource_id: UUIDy, do_print: bool = False) -> None:  # noqa: FBT001, FBT002
    """新規登録."""
    q = sysnet2cypher(sn)
    if len(q.splitlines()) <= 1:  # create対象なし
        return
    if do_print:
        print()  # noqa: T201
        print(q)  # noqa: T201
    db.cypher_query(q, params={"uid": to_uuid(resource_id).hex})
