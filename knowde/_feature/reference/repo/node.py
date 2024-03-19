from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared import query_cypher
from knowde._feature.reference.domain import Reference
from knowde._feature.reference.domain.domain import Author, ReferenceGraph
from knowde._feature.reference.domain.graph_path import GraphPaths, GraphReplacer

from .label import author_util, ref_util

if TYPE_CHECKING:
    from uuid import UUID


def add_root(name: str) -> Reference:
    return ref_util.create(name=name).to_model()


def change_name(ref_id: UUID, name: str) -> Reference:
    lb = ref_util.find_by_id(ref_id).label
    lb.name = name
    return Reference.to_model(lb.save())


def add_part(parent_id: UUID, name: str) -> Reference:
    parent = ref_util.find_by_id(parent_id)
    part = ref_util.create(name=name)
    part.label.parent.connect(parent.label)
    return part.to_model()


def add_author(
    name: str,
    ref: Reference | None = None,
) -> Author:
    a = author_util.create(name=name)
    if ref is not None:
        r = ref_util.find_by_id(ref.valid_uid)
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
    roots = results.get("root", convert=Reference.to_model)
    rpaths = GraphPaths(init=roots)
    rpaths.add(
        results.get(
            "tree",
            convert=Reference.to_models,
            row_convert=lambda row: row.nodes,
        ),
    )

    author_replacer = GraphReplacer(
        init=results.get("p"),
        to_domain=lambda row: Reference.to_model(row.start_node),
        to_range=lambda row: Author.to_model(row.end_node),
    )
    author_replacer(rpaths.G)
    return ReferenceGraph(G=rpaths.G, roots=roots)
