"""sync router test."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from knowde.complex.auth.repo.client import (
    AuthArgs,
    AuthPost,
)
from knowde.complex.entry.namespace.sync import Anchor
from knowde.complex.entry.namespace.test_namespace import files  # noqa: F401
from knowde.feature.api import api
from knowde.primitive.config.env import Settings

if TYPE_CHECKING:
    from pathlib import Path


def test_sync_router(files: tuple[Anchor, list[Path]]) -> None:  # noqa: F811
    """Sync コマンドでの想定."""
    anchor, paths = files
    client = TestClient(api)
    p = AuthPost(client=client.post)
    info = AuthArgs(email="user@example.com", password="password")  # noqa: S106
    res = p.register(info)
    res = p.login(info)
    token = res.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    meta = anchor.to_metas(paths)
    s = Settings()
    res = s.post(
        "/namespace",
        headers=h,
        client=client.post,
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
        s.url("/upload"),
        headers=h,
        files=reqfiles,
    )
    [f.close() for f in op]
    assert res.is_success
