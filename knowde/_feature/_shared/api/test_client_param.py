"""自身で作成したAPIを呼び出す.

- clientの型注釈をちゃんとする
- APIRouterにpath paramを定義
- path paramの値をkwargsから取得
- query paramの値をkwargsから取得
- bodyの値をkwargsから取得
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from knowde._feature._shared.api.client_param import (
    BodyParam,
    PathParam,
    QueryParam,
)
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.generate_req import StatusCodeGrant


def to_client(router: APIRouter) -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(router)
    return TestClient(api)


def test_bind_path_param() -> None:
    """APIRouterにpath paramを定義."""
    grant = StatusCodeGrant(router=Endpoint.Test.create_router())
    uid = uuid4()

    def _f(uid: UUID) -> UUID:
        return uid

    p = PathParam(name="uid")
    assert p.var == "{uid}"
    p.bind(grant.to_get, _f)
    res = to_client(grant.router).get(f"/tests/{uid}")
    assert UUID(res.json()) == uid


@pytest.mark.parametrize(
    ("name", "prefix", "expected"),
    [
        ("var", "", "/{var}"),
        ("var", "/", "/{var}"),
        ("var", "//", "/{var}"),
        ("var", "base", "/base/{var}"),
        ("var", "/base", "/base/{var}"),
        ("var", "base/", "/base/{var}"),
        ("var", "/base/", "/base/{var}"),
    ],
)
def test_path(name: str, prefix: str, expected: str) -> None:
    """/が2回続くような不正なパスが作られない."""
    assert PathParam(name=name, prefix=prefix).path == expected


def test_get_path_value_from_kwargs() -> None:
    uid = uuid4()
    kwargs = {"uid": uid}
    p = PathParam(name="uid")
    assert p.getvalue(kwargs) == uid


def test_get_query_param_value_from_kwargs() -> None:
    """結合できる."""
    uid1 = uuid4()
    uid2 = uuid4()
    kwargs = {"v1": uid1, "v2": uid2, "v3": "dummy"}

    qp1 = QueryParam(name="v1")
    assert qp1.getvalue(kwargs) == {"v1": uid1}

    qp2 = QueryParam(name="v2")
    qp = qp1.combine(qp2)
    assert qp.getvalue(kwargs) == {"v1": uid1, "v2": uid2}


def test_body_param_value_from_kwargs() -> None:
    """annotationと無関係な値を無視."""

    class OneModel(BaseModel, frozen=True):
        v1: str

    s = "string"
    kwargs = {"v1": s, "dummy": "xxx"}
    bp = BodyParam(annotation=OneModel)
    assert bp.getvalue(kwargs) == {"v1": s}
