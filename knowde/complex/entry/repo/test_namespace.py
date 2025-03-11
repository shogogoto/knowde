"""test repo."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TypeAlias

import pytest

from knowde.complex.entry.category.folder import NameSpace
from knowde.complex.entry.category.folder.repo import (
    fetch_namespace,
)
from knowde.complex.entry.repo import (
    save_resource,
    sync_namespace,
)
from knowde.complex.entry.repo.sync import path2meta
from knowde.primitive.user.repo import LUser


def write_text(p: Path, txt: str) -> Path:  # noqa: D103
    p.write_text(dedent(txt))
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

    title1 = write_text(
        sub11 / "title1.txt",
        """
        # title1
            @author John Due
            @published H20/11/1
        ## xxx
            x
            y
            z
        """,
    )

    title2 = write_text(
        sub11 / "title2.txt",
        """
        # title2
            @author hanako
            @published S20/11/1
        ## abc
            janne da arc
        """,
    )
    direct = write_text(
        base_path / "direct.txt",
        """
        # direct
            @published 1999/12/31
        """,
    )
    fail = write_text(
        sub2 / "fail.txt",
        """
        # fail
            @author nanashi
        ## hatena
            blog
                -> xxx
               -> yyy
        """,
    )

    return base_path, [title1, title2, direct, fail]


@pytest.fixture()
def files(tmp_path: Path) -> tuple[Path, list[Path]]:  # noqa: D103
    return create_test_files(tmp_path)


@pytest.fixture()
def u() -> LUser:  # noqa: D103
    return LUser().save()


Fixture: TypeAlias = tuple[LUser, Path, list[Path], NameSpace]


@pytest.fixture()
def setup(u: LUser, files: tuple[Path, list[Path]]) -> Fixture:  # noqa: D103
    meta = path2meta(*files)
    ns = fetch_namespace(u.uid)
    for m in meta.root:
        save_resource(m, ns)
    ns = fetch_namespace(u.uid)
    anchor, paths = files
    return u, anchor, paths, ns


def test_save_new(setup: Fixture) -> None:
    """全て新規."""
    _, _, _, ns = setup
    assert ns.get_or_none("sub1")
    assert ns.get_or_none("sub1", "sub11")
    assert ns.get_or_none("sub1", "sub11", "# title1")
    assert ns.get_or_none("sub1", "sub11", "# title2")
    assert ns.get_or_none("# direct")


def test_save_halfway_exists_folder(setup: Fixture) -> None:
    """途中のフォルダまで既存."""
    u, anchor, paths, ns = setup  # 既存作成
    sub = paths[0].parent  # anchor / sub1 / sub11

    p = sub / "new1" / "new2"
    p.mkdir(parents=True)
    new = write_text(
        p / "added.txt",
        """
        # added
            @author GTO
        ## heading
            a
            b
            c
        """,
    )
    meta = path2meta(anchor, [*paths, new])
    ns = fetch_namespace(u.uid)
    for m in meta.root:
        save_resource(m, ns)
    ns = fetch_namespace(u.uid)
    assert ns.get_or_none("sub1")
    assert ns.get_or_none("sub1", "sub11")
    assert ns.get_or_none("sub1", "sub11", "# title1")
    assert ns.get_or_none("# direct")
    assert ns.get_or_none("sub1", "sub11", "new1", "new2", "# added")


def test_save_update_exists(setup: Fixture) -> None:
    """既存リソースの更新."""
    u, anchor, paths, ns = setup
    tgt = paths[0]
    tgt = write_text(
        tgt,
        """
        # title1
            @author John Due
            @published H20/11/1
        ## xxx -> aaa
            x -> a
            y -> b
            z -> c
        """,
    )
    assert ns.get("sub1", "sub11", "# title1").txt_hash != hash(tgt.read_text())
    paths[0] = tgt
    meta = path2meta(anchor, paths)
    for m in meta.root:
        save_resource(m, ns)
    ns = fetch_namespace(u.uid)
    assert ns.get("sub1", "sub11", "# title1").txt_hash == hash(tgt.read_text())


def test_sync_move(setup: Fixture) -> None:
    """移動したResourceを検知."""
    u, anchor, paths, ns = setup
    tgt = paths[0]
    paths[0] = tgt.rename(tgt.parent.parent / tgt.name)
    meta = path2meta(anchor, paths)
    assert ns.get_or_none("sub1", "sub11", "# title1")
    d = sync_namespace(meta, ns)

    ns = fetch_namespace(u.uid)
    assert ns.get_or_none("sub1", "sub11", "# title1") is None  # たまに失敗
    assert ns.get_or_none("sub1", "# title1")
    assert list(d.keys()) == [("sub1", "# title1")]
