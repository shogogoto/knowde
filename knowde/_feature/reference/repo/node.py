from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from knowde._feature._shared import query_cypher
from knowde._feature.reference.domain import Reference
from knowde._feature.reference.domain.domain import Author, ReferenceGraph

from .label import author_util, ref_util

if TYPE_CHECKING:
    from uuid import UUID

    from neomodel import NeomodelPath


def add_root(name: str) -> Reference:
    return ref_util.create(name=name).to_model()


def add_part(parent_id: UUID, name: str) -> Reference:
    parent = ref_util.find_one(parent_id)
    part = ref_util.create(name=name)
    part.label.parent.connect(parent.label)
    return part.to_model()


def add_author(
    name: str,
    ref: Reference | None = None,
) -> Author:
    a = author_util.create(name=name)
    if ref is not None:
        r = ref_util.find_one(ref.valid_uid)
        r.label.author.connect(a.label)
    return a.to_model()


def find_roots() -> ReferenceGraph:
    results = query_cypher(
        """
        MATCH (root:Reference)
        WHERE NOT (root)-[:INCLUDED*1]->(:Reference)
        OPTIONAL MATCH p = (root)<-[:WROTE*1]-(author:Author)
        OPTIONAL MATCH tree = (root)<-[rel:INCLUDED*]-(child:Reference)
        RETURN root, p, tree
        """,
    )
    g_ref = nx.DiGraph()
    roots = [Reference.to_model(lb) for lb in results.get("root")]
    g_ref.add_nodes_from(roots)
    for row in results.get("tree"):
        x: NeomodelPath = row
        models = ref_util.to_labels(x.nodes).to_model()
        nx.add_path(g_ref, models)

    g_author = nx.DiGraph()
    for row in results.get("p"):
        p: NeomodelPath = row
        path = [
            Reference.to_model(p.start_node),
            Author.to_model(p.end_node),
        ]
        nx.add_path(g_author, path)

    mapping = {}
    for ref in g_ref.nodes:
        if ref in g_author:
            mapping[ref] = ref.model_copy(
                update={
                    "authors": tuple(g_author.successors(ref)),
                    # "authors": g_author.successors(ref),
                },
            )
    nx.relabel_nodes(g_ref, mapping, copy=False)
    return ReferenceGraph(G=g_ref, roots=roots)


# def find_reference(uid: UUID) -> ReferenceGraph:
#     result = query_cypher(
#         """
#         MATCH (tgt:Reference) WHERE tgt.uid=$uid
#         OPTIONAL MATCH p = (tgt)<-[rel:INCLUDED*]-(child:Reference)
#         RETURN p
#         """,
#         params={"uid": uid.hex},
#         resolve_objects=True,
#     )
#     g = nx.DiGraph()
#     for row in result.get("p"):
#         x: NeomodelPath = row
#         models = ref_util.to_labels(x.nodes).to_model()
#         nx.add_path(g, models)
#     return ReferenceGraph(G=g, uid=uid)
