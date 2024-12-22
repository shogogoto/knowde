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

from knowde.primitive.__core__.api.endpoint import Endpoint, router2get

from .api_param import (
    APIBody,
    APIPath,
    APIQuery,
)


def _to_client(router: APIRouter) -> TestClient:
    """Test util."""
    api = FastAPI()
    api.include_router(router)
    return TestClient(api)


def test_bind_path_param() -> None:
    """APIRouterにpath paramを定義."""
    router = Endpoint.Test.create_router()
    uid = uuid4()

    def _f(uid: UUID) -> UUID:
        return uid

    p = APIPath(name="uid", prefix="")
    assert p.var == "{uid}"
    router2get(router, _f, p.path)
    res = _to_client(router).get(f"/tests/{uid}")
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
    assert APIPath(name=name, prefix=prefix).path == expected


def test_get_path_value_from_kwargs() -> None:  # noqa: D103
    uid = uuid4()
    kwargs = {"uid": uid}
    p = APIPath(name="uid", prefix="")
    assert p.getvalue(kwargs) == f"/{uid}"


def test_get_query_param_value_from_kwargs() -> None:
    """結合できる."""
    uid1 = uuid4()
    uid2 = uuid4()
    kwargs = {"v1": uid1, "v2": uid2, "v3": "dummy"}

    qp1 = APIQuery(name="v1")
    assert qp1.getvalue(kwargs) == {"v1": uid1}

    qp = qp1.add(name="v2")
    assert qp.getvalue(kwargs) == {"v1": uid1, "v2": uid2}


def test_body_param_value_from_kwargs() -> None:
    """annotationと無関係な値を無視."""

    class OneModel(BaseModel, frozen=True):
        v1: str

    s = "string"
    kwargs = {"v1": s, "dummy": "xxx"}
    bp = APIBody(annotation=OneModel)
    assert bp.getvalue(kwargs) == {"v1": s}


def test_complex_path_param() -> None:
    """PathParamの合成."""
    p1 = APIPath(name="var1", prefix="prefix1")
    p = p1.add(name="var2", prefix="prefix2")

    d = {"var1": "xxx", "var2": "yyy"}
    assert p.getvalue(d) == "/prefix1/xxx/prefix2/yyy"
    assert p.path == "/prefix1/{var1}/prefix2/{var2}"
