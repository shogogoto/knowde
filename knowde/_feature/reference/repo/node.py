from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import networkx as nx

from knowde._feature._shared import query_cypher
from knowde._feature.reference.domain.domain import ReferenceGraph

from .label import ref_util

if TYPE_CHECKING:
    from uuid import UUID

    from neomodel import NeomodelPath

    from knowde._feature.reference.domain import Reference


def add_reference(name: str) -> Reference:
    return ref_util.create(name=name).to_model()


def add_part(parent_id: UUID, name: str) -> Reference:
    parent = ref_util.find_one(parent_id)
    part = ref_util.create(name=name)
    part.label.parent.connect(parent.label)
    return part.to_model()


def find_roots() -> list[Reference]:
    results, meta = query_cypher(
        """
        MATCH (r:Reference)
        WHERE NOT (r)-[:INCLUDED*1]->(:Reference)
        RETURN r
        """,
    )
    return ref_util.to_labels(
        list(itertools.chain.from_iterable(results)),
    ).to_model()


def find_reference(uid: UUID) -> ReferenceGraph:
    results, meta = query_cypher(
        """
        MATCH (tgt:Reference) WHERE tgt.uid=$uid
        MATCH p = (tgt)<-[rel:INCLUDED*]-(child:Reference)
        RETURN p
        """,
        params={"uid": uid.hex},
        resolve_objects=True,
    )
    g = nx.DiGraph()
    for row in results:
        x: NeomodelPath = row[0]
        models = ref_util.to_labels(x.nodes).to_model()
        nx.add_path(g, models)
    return ReferenceGraph(G=g, uid=uid)
