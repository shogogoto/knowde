from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from neomodel import StringProperty
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel, ModelList
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature._shared.integrated_interface.generate import (
    create_get_generator,
)
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil

if TYPE_CHECKING:
    from requests_mock.mocker import Mocker


class LOne(LBase):
    __label__ = "One"
    name = StringProperty()
    value = StringProperty()


class OneParam(BaseModel, frozen=True):
    name: str
    value: str


class OneModel(OneParam, DomainModel, frozen=True):
    pass


# End

util = LabelUtil(label=LOne, model=OneModel)


class _CompleteParam(BaseModel):
    pref_uid: str


def test_generate_completion(requests_mock: Mocker) -> None:
    m = util.create(name="n", value="v").to_model()

    def _api_func(p: _CompleteParam) -> OneModel:
        return util.complete(p.pref_uid).to_model()

    r = APIRouter(prefix=Endpoint.Test.prefix)
    api = FastAPI()
    _, gen_get = create_get_generator(
        r,
        t_in=_CompleteParam,
        t_out=OneModel,
        func=_api_func,
        relative="/completion",
    )
    api.include_router(r)
    client = TestClient(api)
    pref_uid = m.valid_uid.hex[0]
    res = client.get(url="/tests/completion", params={"pref_uid": pref_uid})
    assert OneModel.model_validate(res.json()) == m

    requests_mock.get(
        url=f"/tests/completion?pref_uid={pref_uid}",
        json=res.json(),
    )
    assert gen_get(OneModel.model_validate)(pref_uid=pref_uid) == m


def test_generate_list(requests_mock: Mocker) -> None:
    m1 = util.create(name="n", value="v").to_model()
    m2 = util.create(name="n", value="v").to_model()

    def _api_func() -> list[OneModel]:
        return util.find_all().to_model()

    r = APIRouter(prefix=Endpoint.Test.prefix)
    api = FastAPI()
    _, gen_get = create_get_generator(
        r,
        t_in=None,
        t_out=list[OneModel],
        func=_api_func,
    )
    api.include_router(r)
    client = TestClient(api)
    res = client.get(url="/tests")
    assert res.json() == ModelList(root=[m1, m2]).model_dump(mode="json")

    requests_mock.get(
        url="/tests",
        json=res.json(),
    )
    assert gen_get(
        encoder=lambda data: [OneModel.model_validate(e) for e in data],
    )() == [m1, m2]
