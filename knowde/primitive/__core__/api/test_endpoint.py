"""APIエンドポイントtest."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, FastAPI, status
from fastapi.testclient import TestClient
from neomodel import StringProperty
from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model

from knowde.primitive.__core__.api.endpoint import router2get, router2put, router2tpost
from knowde.primitive.__core__.domain import Entity
from knowde.primitive.__core__.label_repo.base import LBase
from knowde.primitive.__core__.label_repo.util import LabelUtil
from knowde.primitive.__core__.typeutil import inject_signature

if TYPE_CHECKING:
    from requests_mock.mocker import Mocker

"""1つの関数からapiとrequest, commandを生成できるようにしたい.

repo -> api, req
ボイラープレートを削除したい
関数 = repositoryを想定

問題
- 不定のutil関数の引数が不定でありAPI定義に失敗

feature
- restの簡単指定


標準的なAPI, CLIのセットを生成したい
"""


class LTest(LBase):  # noqa: D101
    __label__ = "Test"
    name = StringProperty()
    value = StringProperty()


class OneParam(BaseModel, frozen=True):  # noqa: D101
    name: str
    value: str | None = None


class OneModel(OneParam, Entity, frozen=True):  # noqa: D101
    pass


util = LabelUtil(label=LTest, model=OneModel)


def _to_client(router: APIRouter) -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(router)
    return TestClient(api)


PREFIX = "/tests"


def test_fail_with_lost_type() -> None:
    """Partialなど生成した型情報はAPI定義時に喪失してエラーになる."""
    OneParamPartial = create_partial_model(OneParam)  # noqa: N806

    def change(_uid: UUID, _p: OneParamPartial) -> OneModel:
        ...

    r = APIRouter(prefix=PREFIX)
    router2put(r, change, path="/{uid}")


def test_put(requests_mock: Mocker) -> None:
    """Partialなど生成した型情報が失われるため、型注入で補う.

    Pathパラメータが認識されたかもチェック.
    """
    OneParamPartial = create_partial_model(OneParam)  # noqa: N806

    def change(uid: UUID, p: OneParamPartial) -> OneModel:
        lb = util.find_by_id(uid).label
        for k, v in p.model_dump().items():
            if v is not None:
                setattr(lb, k, v)
        return OneModel.to_model(lb.save())

    r = APIRouter(prefix=PREFIX)
    req = router2put(
        r,
        inject_signature(change, [UUID, OneParam], OneModel),
    )
    m = util.create(name="pre").to_model()
    res = _to_client(r).put(url=f"{PREFIX}/{m.valid_uid}", json={"name": "post"})
    assert res.status_code == status.HTTP_200_OK
    res = _to_client(r).put(
        url=f"{PREFIX}/{m.valid_uid}/unknown",
        json={"name": "post"},
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND

    requests_mock.put(url=f"{PREFIX}/{m.valid_uid}", json={"name": "n2"})
    assert req(relative=f"{m.valid_uid}").json()["name"] == "n2"


def test_post(requests_mock: Mocker) -> None:
    """リソースの新規作成APIの生成."""

    def f(p: OneParam) -> OneModel:
        return util.create(**p.model_dump()).to_model()

    r = APIRouter(prefix=PREFIX)
    req = router2tpost(r, f)

    res = _to_client(r).post(url=PREFIX, json={"name": "n1"})
    assert res.status_code == status.HTTP_201_CREATED
    m1 = OneModel.model_validate(res.json())
    assert m1.name == "n1"

    requests_mock.post(url=PREFIX, json={"name": "n2"})
    assert req().json()["name"] == "n2"


def test_generate_get(requests_mock: Mocker) -> None:
    """取得APIの生成."""

    def f() -> list[OneModel]:
        return util.find().to_model()

    r = APIRouter(prefix=PREFIX)
    req = router2get(r, f)

    res = _to_client(r).get(url=PREFIX)
    assert res.status_code == status.HTTP_200_OK

    requests_mock.get(url=PREFIX, json=[])
    assert req().json() == []


def test_generate_get_with_param(requests_mock: Mocker) -> None:
    """クエリパラメータで検索."""

    def f(pref_uid: str) -> OneModel:
        return util.complete(pref_uid).to_model()

    r = APIRouter(prefix=PREFIX)
    req = router2get(r, f, path="/completion")

    m = util.create(name="completion").to_model()
    pref_uid = m.valid_uid.hex[0]
    params = {"pref_uid": pref_uid}
    pref_uid = m.valid_uid.hex[0]
    res = _to_client(r).get(
        url=f"{PREFIX}/completion",
        params=params,
    )
    assert res.status_code == status.HTTP_200_OK
    assert OneModel.model_validate(res.json()) == m

    requests_mock.get(url=f"{PREFIX}/completion?pref_uid={pref_uid}")
    assert (
        req(relative=f"/completion?pref_uid={pref_uid}").status_code
        == status.HTTP_200_OK
    )
