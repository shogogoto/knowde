from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from neomodel import StringProperty
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel, ModelList
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature._shared.integrated_interface.basic_method import (
    create_basic_methods,
)
from knowde._feature._shared.integrated_interface.generate import (
    create_request_generator,
)
from knowde._feature._shared.integrated_interface.types import CompleteParam
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil

from .types import HttpType

if TYPE_CHECKING:
    from requests_mock.mocker import Mocker


class LOne(LBase):
    __label__ = "One"
    name = StringProperty()
    value = StringProperty()


class OneParam(BaseModel, frozen=True):
    name: str
    value: str | None = None


class OneModel(OneParam, DomainModel, frozen=True):
    pass


util = LabelUtil(label=LOne, model=OneModel)
methods = create_basic_methods(util)


def test_generate_completion(requests_mock: Mocker) -> None:
    m = util.create(name="n", value="v").to_model()
    api = FastAPI()
    r, gen_get = create_request_generator(
        APIRouter(prefix=Endpoint.Test.prefix),
        t_in=CompleteParam,
        t_out=OneModel,
        api_impl=methods.complete,
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
    api = FastAPI()
    r, gen_get = create_request_generator(
        APIRouter(prefix=Endpoint.Test.prefix),
        t_in=None,
        t_out=list[OneModel],
        api_impl=methods.ls,
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


def test_generate_add(requests_mock: Mocker) -> None:
    api = FastAPI()

    def impl(p: OneParam) -> OneModel:
        return util.create(**p.model_dump()).to_model()

    r, gen_post = create_request_generator(
        APIRouter(prefix=Endpoint.Test.prefix),
        t_in=OneParam,
        t_out=OneModel,
        api_impl=impl,
        ht=HttpType.POST,
    )
    # 確認用にgetを定義
    _, gen_get = create_request_generator(
        r,
        t_in=None,
        t_out=list[OneModel],
        api_impl=methods.ls,
    )
    api.include_router(r)
    client = TestClient(api)

    res1 = client.post(url="/tests", json={"name": "n1", "value": "v1"})
    res2 = client.post(url="/tests", json={"name": "n2"})
    res = client.get(url="/tests")
    assert res.json() == [res1.json(), res2.json()]

    requests_mock.post(
        url="/tests",
        json={"name": "n3"},
    )
    m = gen_post(encoder=OneModel.model_validate)(OneParam(name="dummy"))
    assert m.name == "n3"


# def test_generate_ch(requests_mock: Mocker) -> None:
#     pass
