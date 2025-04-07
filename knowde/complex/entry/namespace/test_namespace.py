"""test repo."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from knowde.complex.entry import NameSpace
from knowde.complex.entry.category.folder.repo import (
    fetch_namespace,
)
from knowde.complex.entry.namespace import (
    save_resource,
    sync_namespace,
)
from knowde.primitive.user.repo import LUser

from .sync import Anchor, filter_parsable


def write_text(p: Path, txt: str) -> Path:  # noqa: D103
    p.write_text(dedent(txt))
    return p


def create_test_files(base_path: Path) -> tuple[Anchor, list[Path]]:
    """sync用テストファイル群."""
    subs = [
        base_path / "sub1" / "sub11",
        base_path / "sub1" / "sub12",
        base_path / "sub2",
    ]
    [s.mkdir(parents=True) for s in subs]
    sub11, _sub12, sub2 = subs

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
    return Anchor(base_path), [title1, title2, direct, fail]


@pytest.fixture
def files(tmp_path: Path) -> tuple[Anchor, list[Path]]:  # noqa: D103
    return create_test_files(tmp_path)


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser().save()


type Fixture = tuple[LUser, Anchor, list[Path], NameSpace]


@pytest.fixture
def setup(u: LUser, tmp_path: Path) -> Fixture:  # noqa: D103
    anchor, paths = create_test_files(tmp_path)
    meta = anchor.to_metas(filter_parsable(*paths))
    ns = fetch_namespace(u.uid)
    for m in meta.root:
        save_resource(m, ns)
    ns = fetch_namespace(u.uid)
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
    meta = anchor.to_metas(filter_parsable(*[*paths, new]))
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
    meta = anchor.to_metas(filter_parsable(*paths))
    for m in meta.root:
        save_resource(m, ns)
    ns = fetch_namespace(u.uid)
    assert ns.get("sub1", "sub11", "# title1").txt_hash == hash(tgt.read_text())


def test_sync_move(setup: Fixture) -> None:
    """移動したResourceを検知."""
    u, anchor, paths, ns = setup
    tgt = paths[0]
    paths[0] = tgt.rename(tgt.parent.parent / tgt.name)  # 2階上に移動
    meta = anchor.to_metas(filter_parsable(*paths))
    assert ns.get_or_none("sub1", "sub11", "# title1")
    uplist = sync_namespace(meta, ns)

    ns = fetch_namespace(u.uid)
    assert ns.get_or_none("sub1", "sub11", "# title1") is None  # たまに失敗
    assert ns.get_or_none("sub1", "# title1")
    assert [anchor / p for p in uplist] == [paths[0]]


# def test_duplicated_title(setup: Fixture) -> None:
#     """重複したタイトルを検知."""
#     _u, _anchor, paths, ns = setup
#     nxprint(ns.g)
#     m = ResourceMeta(title="# title3")  # 既存タイトル
#     save_or_move_resource(m, ns)
#     tgt = paths[0]
#     nxprint(ns.g)
#     m = ResourceMeta(title="# title3", path=("sub1", "xxx"))  # 既存タイトル
#     save_or_move_resource(m, ns)
#     nxprint(ns.g)
#     # raise AssertionError
#     # paths[0] = tgt.rename(tgt.parent.parent / tgt.name)
#     # meta = anchor.to_metas(filter_parsable(*paths))
#     # assert ns.get_or_none("sub1", "sub11", "# title1")
#     # uplist = sync_namespace(meta, ns)

#     # ns = fetch_namespace(u.uid)
#     # assert ns.get_or_none("sub1", "sub11", "# title1") is None  # たまに失敗
#     # assert ns.get_or_none("sub1", "# title1")
#     # assert [anchor / p for p in uplist] == [paths[0]]
