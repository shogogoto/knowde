"""非pydanticデータ型を対応させる."""
from __future__ import annotations

from collections.abc import Hashable
from typing import Annotated, Any
from uuid import UUID, uuid4

import networkx as nx
from neomodel import StructuredNode
from pydantic import (
    BaseModel,
    Field,
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)


def _validate_neomodel(
    v: Any,
    info: ValidationInfo,
) -> StructuredNode:
    if isinstance(v, StructuredNode):
        return v
    raise TypeError


NeoModel = Annotated[
    StructuredNode,
    PlainValidator(_validate_neomodel),
    PlainSerializer(lambda x: x.__properties__),
]


def _validate_graph(v: Any, info: ValidationInfo) -> nx.DiGraph:
    if isinstance(v, dict):
        return nx.node_link_graph(v)
    if isinstance(v, nx.DiGraph):
        return v
    raise TypeError


class EdgeData(BaseModel):
    """for fastapi schema."""

    source: str
    target: str


class GraphData(BaseModel):
    """for fastapi schema."""

    directed: bool
    edges: list[EdgeData]
    graph: dict
    multigraph: bool
    nodes: list[dict[str, str]]


NXGraph = Annotated[
    nx.DiGraph,
    PlainValidator(_validate_graph),
    PlainSerializer(
        lambda x: nx.node_link_data(x, edges="edges"),
        return_type=GraphData,
    ),
]


class Duplicable(BaseModel, frozen=True):
    """同一文字列を重複して登録するためにuuidを付与.

    区分け文字 みたいな区切りを作るためだけの無意味な文字列の扱いは?
    """

    n: Hashable
    uid: UUID = Field(default_factory=uuid4)

    def __str__(self) -> str:  # noqa: D105
        return str(self.n)

    def __repr__(self) -> str:
        """Class representation."""
        return f"Dupl({self})"
