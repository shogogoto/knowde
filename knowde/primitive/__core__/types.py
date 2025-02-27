"""非pydanticデータ型を対応させる."""
from __future__ import annotations

from typing import Annotated, Any, Hashable
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
    v: Any,  # noqa: ANN401
    info: ValidationInfo,  # noqa: ARG001
) -> StructuredNode:
    if isinstance(v, StructuredNode):
        return v
    raise TypeError


NeoModel = Annotated[
    StructuredNode,
    PlainValidator(_validate_neomodel),
    PlainSerializer(lambda x: x.__properties__),
]


def _validate_graph(v: Any, info: ValidationInfo) -> nx.DiGraph:  # noqa: ARG001 ANN401
    if isinstance(v, nx.DiGraph):
        return v
    raise TypeError


NXGraph = Annotated[
    nx.DiGraph,
    PlainValidator(_validate_graph),
    PlainSerializer(lambda x: nx.node_link_data(x)),
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
