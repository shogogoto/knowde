from __future__ import annotations

from typing import Annotated, Any, Final, Optional

from networkx import DiGraph, tree_data
from networkx.convert import nx
from pydantic import (
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
)

from knowde._feature._shared import DomainModel


class Reference(DomainModel, frozen=True):
    """nodeとしてのモデル. relを含まない."""

    name: str
    authors: set[Author] | None = None


class Author(DomainModel, frozen=True):
    name: str
    # birthday: date


def validate(v: Any, info: ValidationInfo) -> DiGraph:  # noqa: ARG001 ANN401
    if isinstance(v, DiGraph):
        return v
    raise TypeError


Graph = Annotated[
    DiGraph,
    PlainValidator(validate),
    PlainSerializer(lambda x: nx.node_link_graph(x)),
]


class ReferenceGraph(DomainModel, frozen=True):
    G: Graph

    @property
    def root(self) -> Reference:
        return next(
            filter(
                lambda x: x.uid == self.valid_uid,
                self.G.nodes,
            ),
        )

    def tree(
        self,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
    ) -> Reference:
        td = tree_data(self.G, root=self.root, ident="ref")
        k: Final[str] = "children"

        def _convert(d: dict[str, Reference]) -> Reference:
            _d = d["ref"].model_dump(
                include=include,
                exclude=exclude,
            )
            if k in d:
                _d[k] = [_convert(child) for child in d[k]]
                return RefComposite.model_validate(_d)
            return RefLeaf.model_validate(_d)

        return _convert(td)


class RefComposite(Reference, frozen=True):
    children: list[RefComposite | RefLeaf]
    author: Author | None = None


class RefLeaf(Reference, frozen=True):
    index: int | None = None
