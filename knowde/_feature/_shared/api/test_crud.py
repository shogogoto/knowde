from fastapi import FastAPI
from fastapi.testclient import TestClient
from neomodel import StringProperty
from starlette.status import HTTP_404_NOT_FOUND

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.errors.errors import ErrorHandlingMiddleware
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil

from .crud import CRUDRouter


class LTestLabel(LBase):
    """for testing."""

    __label__ = "TestingApi"
    prop = StringProperty()


class OneModel(DomainModel, frozen=True):
    prop: str


util = LabelUtil(label=LTestLabel, model=OneModel)

r = CRUDRouter(util=util).create(prefix="/testing", tags=["testing"])
api = FastAPI()
api.add_middleware(ErrorHandlingMiddleware)
api.include_router(r)
client = TestClient(api)


def test_get() -> None:
    res = client.get(url="/testing")
    assert len(res.json()) == 0

    one = util.create(prop="p").to_model()
    res = client.get(url="/testing")
    assert len(res.json()) == 1

    # hit 1
    res = client.get(
        url="/testing/completion",
        params={
            "pref_uid": one.valid_uid.hex[0],
        },
    )
    assert OneModel.model_validate(res.json()) == one

    res = client.get(
        url="/testing/completion",
        params={
            "pref_uid": "eeee",  # not matching
        },
    )
    assert res.status_code == HTTP_404_NOT_FOUND

    client.delete(url=f"/testing/{one.valid_uid}")
    res = client.get(url="/testing")
    assert len(res.json()) == 0
