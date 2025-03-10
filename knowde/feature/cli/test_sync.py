"""sync router test."""
from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from knowde.complex.auth.repo.client import (
    AuthArgs,
    AuthPost,
)
from knowde.complex.resource.repo.sync import path2meta
from knowde.feature.api import api
from knowde.primitive.config.env import Settings

if TYPE_CHECKING:
    from pathlib import Path


def write_text(p: Path, txt: str) -> Path:  # noqa: D103
    s = dedent(txt)
    p.write_text(s)
    return p


def create_test_files(base_path: Path) -> tuple[Path, list[Path]]:
    """sync用テストファイル群."""
    subs = [
        base_path / "sub1" / "sub11",
        base_path / "sub1" / "sub12",
        base_path / "sub2",
    ]
    [s.mkdir(parents=True) for s in subs]
    sub11, sub12, sub2 = subs

    # print(sub11, sub12, sub2)
    title1 = write_text(
        sub11 / "title1.txt",
        """
        # title1
            @author John Due
            @published H20/11/1
        ## aaa
            x
            y
            z
        """,
    )

    direct = write_text(
        base_path / "direct.txt",
        """
        # direct
            @published 1999/12/31
        """,
    )

    return base_path, [title1, direct]


@pytest.fixture()
def test_files(tmp_path: Path) -> tuple[Path, list[Path]]:  # noqa: D103
    return create_test_files(tmp_path)


def test_sync_router(test_files: list[Path]) -> None:
    """Sync コマンドでの想定."""
    client = TestClient(api)
    p = AuthPost(client=client.post)
    info = AuthArgs(email="user@example.com", password="password")  # noqa: S106
    res = p.register(info)
    res = p.login(info)
    token = res.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    anchor, paths = test_files
    data = path2meta(anchor, paths)
    # print(data.model_dump_json(indent=2))
    # data.root.append(ResourceMeta(ti))

    s = Settings()
    _res = s.post(
        "/namespace",
        headers=h,
        client=client.post,
        json=data.model_dump(mode="json"),
    )

    # print(user_id)

    # user 作成
    # ログイン
    # テストファイル用意 anchorの偽装
    # namespace用意
