"""非pydanticデータ型を対応させる."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Annotated, Any
from uuid import UUID, uuid4

import networkx as nx
from neomodel import StringProperty, StructuredNode, UniqueIdProperty
from pydantic import (
    BaseModel,
    Field,
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)

from knowde.shared.nxutil.edge_type import EdgeType

type UUIDy = UUID | str | UniqueIdProperty  # Falsyみたいな
type STRy = str | StringProperty


def to_uuid(uidy: UUIDy) -> UUID:
    """neomodelのuid propertyがstrを返すからUUIDに補正・統一して扱いたい."""
    return UUID(uidy) if isinstance(uidy, (str, UniqueIdProperty)) else uidy


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
        return nx.node_link_graph(v, edges="edges")
    if isinstance(v, nx.DiGraph):
        return v
    raise TypeError


class EdgeData(BaseModel):
    """for fastapi schema."""

    type: EdgeType
    source: str
    target: str
    key: int


class GraphData(BaseModel):
    """for fastapi schema."""

    directed: bool
    edges: list[EdgeData]
    graph: dict
    multigraph: bool
    nodes: list[dict[str, str]]


NXGraph = Annotated[
    nx.DiGraph,
    PlainValidator(_validate_graph, json_schema_input_type=dict),
    PlainSerializer(
        lambda x: nx.node_link_data(x, edges="edges"),
        # lambda x: GraphData.model_validate(nx.node_link_data(x, edges="edges")),
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
