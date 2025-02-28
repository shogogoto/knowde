"""neomodel mapper."""
from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

if TYPE_CHECKING:
    from knowde.complex.resource.category.folder.repo import LFolder


class MFolder(BaseModel, frozen=True):
    """LFolderのgraph用Mapper."""

    name: str
    element_id_property: str | None = None

    @classmethod
    def from_lb(cls, lb: LFolder) -> Self:
        """Map label to hashable object."""
        return _from_lb(lb.name, lb.element_id)

    def __str__(self) -> str:  # noqa: D105
        return self.name

    # def to_lb(self) -> LFolder:
    #     """To neomodel."""
    #     return LFolder(
    #         name=self.name,
    #         element_id_property=self.element_id,
    #     )


@cache
def _from_lb(name: str, element_id_property: str) -> MFolder:
    return MFolder(name=name, element_id_property=element_id_property)
