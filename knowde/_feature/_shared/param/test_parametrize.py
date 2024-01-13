from pydantic import Field

from knowde._feature._shared.api.param import ApiParam
from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.param.parametrize import parametrize


class OneParam(ApiParam, frozen=True):
    p1: str
    p2: int


class Model(DomainModel, frozen=True):
    p3: str
    p4: int


def test_signature() -> None:
    def x(p1: str, p2: int) -> Model:
        return Model(p3=p1, p4=p2)

    f = parametrize(OneParam, x)
    assert f(p1="p1", p2=0) == Model(p3="p1", p4=0)


class Param2(ApiParam, frozen=True):
    p1: str
    p2: int = Field(0, exclude=True)


class Model2(DomainModel, frozen=True):
    p3: str


def test_exclude() -> None:
    def x(p1: str) -> Model2:
        return Model2(p3=p1)

    f = parametrize(Param2, x, exclude=True)
    assert f(p1="p") == Model2(p3="p")
