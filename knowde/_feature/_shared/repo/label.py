from __future__ import annotations

from typing import Annotated, Any, Callable, Generic, Iterator, TypeAlias, TypeVar

from neomodel import DateTimeProperty, StringProperty, StructuredNode, UniqueIdProperty
from pydantic import BaseModel, PlainSerializer, PlainValidator, ValidationInfo

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.timeutil import jst_now


class LBase(StructuredNode):
    __abstract_node__ = True
    uid = UniqueIdProperty()
    name = StringProperty()
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now


def validate(v: Any, info: ValidationInfo) -> LBase:  # noqa: ANN401 ARG001
    if isinstance(v, LBase):
        return v
    raise TypeError


NeoModel = Annotated[
    LBase,
    PlainValidator(validate),
    PlainSerializer(lambda x: x.__properties__),
]

L = TypeVar("L", bound=NeoModel)
M = TypeVar("M", bound=DomainModel)
Converter: TypeAlias = Callable[[L], M]


class Label(BaseModel, Generic[L, M], frozen=True):
    label: L
    convert: Converter[L, M]

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_model(self) -> M:
        return self.convert(self.label)


class Labels(BaseModel, Generic[L, M], frozen=True):
    root: list[L]
    convert: Callable[[L], M]

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self) -> Iterator[L]:
        return iter(self.root)

    def __getitem__(self, i: int) -> L:
        return self.root[i]

    def to_model(self) -> list[M]:
        return [self.convert(lb) for lb in self]
