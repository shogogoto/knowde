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


def find_roots() -> list[Reference]:
    results, _ = query_cypher(
        """
        MATCH (root:Reference)
        WHERE NOT (root)-[:INCLUDED*1]->(:Reference)
        OPTIONAL MATCH p = (root)<-[:WROTE*1]-(author:Author)
        RETURN root, p
        """,
    )
    refs: set[Reference] = set()
    g = nx.DiGraph()
    for row in results:
        refs.add(Reference.to_model(row[0]))
        if row[1] is None:
            continue
        p: NeomodelPath = row[1]
        path = [
            Reference.to_model(p.start_node),
            Author.to_model(p.end_node),
        ]
        nx.add_path(g, path)
    ret = []
    for ref in refs:
        _ref = ref
        if ref in g:
            _authors = set(g.successors(ref))
            _ref = ref.model_copy(update={"authors": _authors})
        ret.append(_ref)
    return ret


def find_reference(uid: UUID) -> ReferenceGraph:
    results, meta = query_cypher(
        """
        MATCH (tgt:Reference) WHERE tgt.uid=$uid
        OPTIONAL MATCH p = (tgt)<-[rel:INCLUDED*]-(child:Reference)
        RETURN p
        """,
        params={"uid": uid.hex},
        resolve_objects=True,
    )
    g = nx.DiGraph()
    for row in results:
        if row[0] is None:
            continue
        x: NeomodelPath = row[0]
        models = ref_util.to_labels(x.nodes).to_model()
        nx.add_path(g, models)
    return ReferenceGraph(G=g, uid=uid)
