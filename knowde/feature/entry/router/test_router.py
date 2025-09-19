"""router test."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from knowde.api import api
from knowde.conftest import mark_async_test
from knowde.feature.entry.namespace.sync import Anchor
from knowde.feature.entry.namespace.test_namespace import files  # noqa: F401
from knowde.feature.knowde import ResourceInfo
from knowde.feature.user.routers.repo.client import (
    AuthPost,
)
from knowde.shared.user.label import LUser

if TYPE_CHECKING:
    from pathlib import Path


def auth_header() -> tuple[TestClient, dict[str, str]]:
    """For fixture."""
    client = TestClient(api)
    p = AuthPost(client=client.post)
    email = "user@example.com"
    password = "password"  # noqa: S105
    res = p.register(email, password)
    res = p.login(email, password)
    token = res.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    return client, h


@mark_async_test()
async def test_sync_router(files: tuple[Anchor, list[Path]]) -> None:  # noqa: F811, RUF029
    """Sync コマンドでの想定."""
    client, h = auth_header()

    anchor, paths = files
    meta = anchor.to_metas(paths)
    res = client.post(
        "/namespace",
        headers=h,
        json=meta.model_dump(mode="json"),
    )

    anchor, _ = files
    reqfiles = []
    op = []
    for _p in res.json():
        p = anchor / _p
        f = p.open("rb")
        op.append(f)
        reqfiles.append(("files", (p.name, f, "application/octet-stream")))
    res = client.post(
        "/resource",
        headers=h,
        files=reqfiles,
    )
    [f.close() for f in op]
    assert res.is_success


@mark_async_test()
async def test_fetch_resource_detail(files: tuple[Anchor, list[Path]]):  # noqa: F811
    """fetch_resource_detailのテスト."""
    client, h = auth_header()
    user = await LUser.nodes.first()
    s = """
    # title
    ## head1
        aaa
        bbb
            ccc

    """

    res = client.post(
        "/resource-text",
        headers=h,
        json={"txt": s, "path": ["a", "b", "c"]},
    )
    assert res.is_success

    uid = res.json()["resource_id"]
    res = client.get(f"/resource/{uid}")
    assert res.is_success
    info = ResourceInfo.model_validate(res.json()["resource_info"])
    assert info.user.id.hex == user.uid
    assert info.resource.uid.hex == uid
