from __future__ import annotations

from typing import Final, Optional

from networkx import tree_data
from pydantic import BaseModel, Field

from knowde._feature._shared import DomainModel, Graph


class Reference(DomainModel, frozen=True):
    """nodeとしてのモデル. relを含まない."""

    name: str
    # authors: list[Author] = Field(default_factory=list)
    authors: tuple[Author, ...] = Field(default_factory=tuple)


class Author(DomainModel, frozen=True):
    name: str
    # birthday: date


class ReferenceGraph(BaseModel, frozen=True):
    G: Graph
    roots: list[Reference]

    def tree(
        self,
        root: Reference,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
    ) -> Reference:
        ident: Final = "ref"
        k: Final[str] = "children"
        td = tree_data(self.G, root=root, ident=ident)

        def _convert(d: dict[str, Reference]) -> Reference:
            _d = d[ident].model_dump(
                include=include,
                exclude=exclude,
            )
            if k in d:
                _d[k] = [_convert(child) for child in d[k]]
                return RefComposite.model_validate(_d)
            return RefLeaf.model_validate(_d)

        return _convert(td)

    def __len__(self) -> int:
        return len(self.roots)


class RefComposite(Reference, frozen=True):
    children: list[RefComposite | RefLeaf]


class RefLeaf(Reference, frozen=True):
    index: int | None = None
