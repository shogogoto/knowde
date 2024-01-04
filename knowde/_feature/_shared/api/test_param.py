from knowde._feature._shared.domain import DomainModel

from .param import ApiParam


class OneParam(ApiParam, frozen=True):
    p1: str
    p2: int


class Model(DomainModel, frozen=True):
    p3: str
    p4: int


def test_signature() -> None:
    def x(p: OneParam) -> Model:
        return Model(p3=p.p1, p4=p.p2)

    f = OneParam.makefunc(x)
    assert f(p1="p1", p2=0) == Model(p3="p1", p4=0)
