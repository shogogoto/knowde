"""db から sysnetを復元."""

from functools import cache
from uuid import UUID

import neo4j
import networkx as nx
from neomodel import db

from knowde.feature.entry.label import LResource
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.primitive.time import WhenNode
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import DUMMY_SENTENCE, Def, KNode
from knowde.feature.parsing.sysnet.sysnode.merged_def import MergedDef
from knowde.feature.parsing.tree2net.directed_edge import DirectedEdgeCollection
from knowde.feature.stats.nxdb import LInterval
from knowde.shared.nxutil.edge_type import Direction, EdgeType
from knowde.shared.types import Duplicable, UUIDy, to_uuid


@cache
def to_sysnode(n: neo4j.graph.Node) -> KNode:
    """neo4jから変換."""
    lb_name = next(iter(n.labels))
    match lb_name:
        case "Sentence" | "Head":
            return n.get("val")
        case "Term":
            return Term.create(n.get("val"))
        case "Resource" | "Entry":
            return n.get("title")
        case "Interval":
            d = dict(n)
            d["n"] = d.pop("val")
            return WhenNode.model_validate(d)
        case _:
            props = n.items()
            raise ValueError(props, lb_name)


def restore_sysnet(resource_uid: UUIDy) -> tuple[SysNet, dict[KNode, UUID]]:  # noqa: PLR0914
    """DBからSysNetを復元."""
    various = "|".join([et.name for et in EdgeType if et != EdgeType.HEAD])
    q = f"""
        MATCH (root:Resource {{uid: $uid}})
        RETURN null as r, root as s, null as e

        // 直下
        UNION
        OPTIONAL MATCH (root)-[r1:HEAD|BELOW]->(top:Head|Sentence)
        RETURN r1 as r, root as s, top as e

        // 見出し
        UNION
        OPTIONAL MATCH (top)-[:HEAD]->*(hs:Head)-[rh:HEAD]->(he:Head)
        RETURN rh as r, hs as s, he as e

        // いろいろ
        UNION
        OPTIONAL MATCH (top)-[:BELOW|SIBLING]->*(n1:Sentence|Interval)
            <-[r2:{various}]-(n2:Sentence|Term|Head)
        return r2 as r, n2 as s, n1 as e

        // 複数名の用語がある場合
        UNION
        MATCH (n2)<-[r3:ALIAS]-(m:Term)
        RETURN r3 as r, m as s, n2 as e
    """
    res = db.cypher_query(q, params={"uid": to_uuid(resource_uid).hex})
    col = DirectedEdgeCollection()
    defs = []
    uids = {}
    for r, _s, _e in res[0]:
        if r is None:  # resource
            if not (_s is None and _e is None):
                rsrc = LResource(**dict(_s))
            continue
        s = to_sysnode(_s)
        e = to_sysnode(_e)
        uids[s] = _s.get("uid")
        uids[e] = _e.get("uid")
        match r.type:
            case "ALIAS" if isinstance(s, Term) and isinstance(e, Term):
                term = Term(names=s.names + e.names)
                defs.append(Def.dummy(term))
            case "DEF" if isinstance(s, Term) and isinstance(e, (str, Duplicable)):
                s2 = Term.create(*s.names, alias=r.get("alias", None))
                d = Def.dummy(s2) if e == DUMMY_SENTENCE else Def(term=s2, sentence=e)
                defs.append(d)
            case x if x == "WHEN" and isinstance(e, LInterval):
                col.append(EdgeType.WHEN, Direction.FORWARD, s, e)
            case x if x in [et.name for et in EdgeType]:
                t = EdgeType.__members__.get(r.type)
                col.append(t, Direction.FORWARD, s, e)
            case _:
                raise ValueError(r, s, e)
    g = nx.MultiDiGraph()
    col.add_edges(g)
    mdefs, stddefs, _ = MergedDef.create_and_parted(defs)
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return SysNet(root=rsrc.title, g=g), uids
