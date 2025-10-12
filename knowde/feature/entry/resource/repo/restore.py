"""db から sysnetを復元."""

from functools import cache
from math import isinf
from uuid import UUID

import neo4j
import networkx as nx
from neomodel.async_.core import AsyncDatabase

from knowde.feature.knowde.repo.cypher import q_call_sent_names
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.primitive.time import WhenNode
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import (
    DUMMY_SENTENCE,
    Def,
    DummySentence,
    KNode,
    add_def_edge,
)
from knowde.feature.parsing.sysnet.sysnode.merged_def import MergedDef
from knowde.feature.parsing.tree2net.directed_edge import DirectedEdgeCollection
from knowde.shared.nxutil.edge_type import Direction, EdgeType
from knowde.shared.types import Duplicable, UUIDy, to_uuid


@cache
def to_sysnode(n: neo4j.graph.Node) -> tuple[KNode, str]:
    """neo4jから変換."""
    lb_name = next(iter(n.labels))
    match lb_name:
        case "Sentence" | "Head":
            retval = n.get("val")
            if retval == DUMMY_SENTENCE:
                retval = DummySentence(uid=n.get("uid"))
        case "Term":
            retval = Term.create(n.get("val"))
        case "Resource" | "Entry":
            retval = n.get("title")
        case "Interval":
            d = dict(n)
            d["n"] = d.pop("val")
            for k in ("start", "end"):  # infはJSONに変換できない
                if isinf(d[k]):
                    d[k] = None
            retval = WhenNode.model_validate(d)
        case _:
            props = n.items()
            raise ValueError(props, lb_name)
    return retval, lb_name


async def restore_tops2(resource_uid: UUIDy) -> tuple[nx.DiGraph, dict[UUID, KNode]]:
    """SysNetを先のHeadまたはSentenceまで復元."""
    q = """
        MATCH (root:Resource {uid: $uid})
        MATCH (root)-[:HEAD]->*(s:Head)-[r:HEAD|BELOW]->(e:Head|Sentence)
        RETURN r, s, e
        UNION
        MATCH (root:Resource {uid: $uid})
        MATCH (root)-[r:HEAD|BELOW]->(e:Head|Sentence)
        RETURN r, root as s, e
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uid": to_uuid(resource_uid).hex},
    )
    g = nx.MultiDiGraph()
    uids = {}
    for row in rows:
        r, s_, e_ = row
        suid = to_uuid(s_.get("uid"))
        euid = to_uuid(e_.get("uid"))
        uids[suid], _ = to_sysnode(s_)
        uids[euid], _ = to_sysnode(e_)
        EdgeType(r.type.lower()).add_edge(g, suid, euid)
    return g, uids


async def restore_tops(resource_uid: UUIDy) -> tuple[nx.DiGraph, str]:
    """SysNetを先のHeadまたはSentenceまで復元."""
    g, uids = await restore_tops2(resource_uid)
    g_relabeled = nx.relabel_nodes(g, uids)
    title = uids[to_uuid(resource_uid)]
    return g_relabeled, title


async def restore_undersentnet2(  # noqa: PLR0914
    resource_uid: UUIDy,
) -> tuple[nx.DiGraph, dict[UUID, KNode], dict[UUID, Term]]:
    """top以下のsentenceやdefのネットワークを復元."""
    various = "|".join([
        et.name for et in EdgeType if et not in {EdgeType.HEAD, EdgeType.DEF}
    ])
    q = f"""
        MATCH (s:Sentence {{resource_uid: $uid}})
        OPTIONAL MATCH (s)-[r:{various}]->(e:Sentence|Interval)
        {q_call_sent_names("s")}
        RETURN s
            , COLLECT([e, r]) as ends
            , COALESCE(names, []) as names
            , alias
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uid": to_uuid(resource_uid).hex},
    )
    g = nx.MultiDiGraph()
    uids: dict[UUID, KNode] = {}
    terms: dict[UUID, Term] = {}
    for row in rows:
        s, ends, names, alias = row
        names = [n.get("val") for n in names]
        sval, _ = to_sysnode(s)
        suid = to_uuid(s.get("uid"))
        uids[suid] = sval
        g.add_node(suid)
        for end in ends:
            e, r = end
            if e is None:
                continue
            euid = to_uuid(e.get("uid"))
            EdgeType(r.type.lower()).add_edge(g, suid, euid)
            uids[euid], _ = to_sysnode(e)
        if len(names) > 0:
            term = Term.create(*names, alias=alias)
            terms[suid] = term
    return g, uids, terms


async def restore_undersentnet(
    resource_uid: UUIDy,
) -> tuple[nx.DiGraph, dict[KNode, UUID]]:
    """top以下のsentenceやdefのネットワークを復元."""
    g22, uids2, terms2 = await restore_undersentnet2(resource_uid)
    for uid, term in terms2.items():
        add_def_edge(g22, uids2[uid], term)
    g2_relabeled = nx.relabel_nodes(g22, uids2)
    return g2_relabeled, {v: k for k, v in uids2.items()}


async def restore_sysnet(resource_uid: UUIDy) -> tuple[SysNet, dict[KNode, UUID]]:
    """SysNetを復元."""
    g1, root = await restore_tops(resource_uid)
    g2, uids = await restore_undersentnet(resource_uid)
    g = nx.compose(g1, g2)
    return SysNet(g=g, root=root), uids


async def restore_sysnet2(resource_uid: UUIDy) -> tuple[SysNet, dict[KNode, UUID]]:  # noqa: PLR0914
    """DBからSysNetを復元."""
    various = "|".join([et.name for et in EdgeType if et != EdgeType.HEAD])
    q = f"""
        MATCH (root:Resource {{uid: $uid}})
        OPTIONAL MATCH (root)-[r1:HEAD|BELOW]->(top:Head|Sentence)
        RETURN r1 as r, root as s, top as e

        // 見出し
        UNION
        MATCH (root:Resource {{uid: $uid}})
        OPTIONAL MATCH (root)-[:HEAD]->*(hs:Head)-[rh:HEAD]->(he:Head)
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
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"uid": to_uuid(resource_uid).hex},
    )

    col = DirectedEdgeCollection()
    defs = []
    uids: dict[KNode, UUID] = {}
    root = ""
    for r, _s, _e in rows:
        if r is None:
            continue
        s, s_name = to_sysnode(_s)
        if s_name == "Resource":
            root = s
        e, _ = to_sysnode(_e)
        s_uid = _s.get("uid")
        if s_uid:
            uids[s] = s_uid
        e_uid = _e.get("uid")
        if e_uid:
            uids[e] = e_uid
        match r.type:
            case "ALIAS" if isinstance(s, Term) and isinstance(e, Term):
                term = Term(names=s.names + e.names)
                defs.append(Def.dummy(term))
            case "DEF" if isinstance(s, Term) and isinstance(e, (str, Duplicable)):
                s2 = Term.create(*s.names, alias=r.get("alias", None))
                d = Def.dummy(s2) if e == DUMMY_SENTENCE else Def(term=s2, sentence=e)
                defs.append(d)
            case x if x == "WHEN" and isinstance(e, WhenNode):
                col.append(EdgeType.WHEN, Direction.FORWARD, s, e)
            case x if x in [et.name for et in EdgeType]:
                t = EdgeType.__members__.get(r.type)
                col.append(t, Direction.FORWARD, s, e)
            case _:
                raise ValueError(r, s, e)
    g = nx.MultiDiGraph()
    col.set_edges(g)
    mdefs, stddefs, _ = MergedDef.create_and_parted(defs)
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return SysNet(root=root, g=g), uids
