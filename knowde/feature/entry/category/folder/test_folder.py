"""test folder."""

from collections.abc import AsyncGenerator

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.category.folder.repo import (
    create_folder,
    create_resource,
    move_folder,
)
from knowde.feature.entry.errors import (
    EntryAlreadyExistsError,
)
from knowde.feature.entry.namespace import fetch_namespace
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> AsyncGenerator[LUser, None]:  # noqa: D103
    return await LUser(email="one@gmail.com").save()


@mark_async_test()
async def test_create_root_folder(u: LUser) -> None:
    """User直下フォルダ."""
    await create_folder(u.uid, "f1")
    fs = await fetch_namespace(u.uid)
    assert fs.roots == ["f1"]


@mark_async_test()
async def test_create_duplicated_root_folder(u: LUser) -> None:
    """User直下の重複フォルダ."""
    await create_folder(u.uid, "f1")
    await create_folder(u.uid, "f2")
    await create_folder(u.uid, "f2", "f1")
    await create_folder(u.uid, "f1")


@mark_async_test()
async def test_create_sub_unexist_parent(u: LUser) -> None:
    """存在しない親の下にフォルダ作ろうとしちゃった."""
    await create_folder(u.uid, "unexist", "f2")


@mark_async_test()
async def test_create_duplicated_sub_folder(u: LUser) -> None:
    """同じ親に対してサブフォルダを複数作る."""
    await create_folder(u.uid, "f1")
    await create_folder(u.uid, "f1", "f2")
    await create_folder(u.uid, "f1", "f2")


@mark_async_test()
async def test_fetch_folderspace(u: LUser) -> None:
    """ユーザー配下のフォルダ空間を一括取得."""
    await create_folder(u.uid, "f1")
    await create_folder(u.uid, "f1", "f2")
    await create_folder(u.uid, "f1", "fff")
    await create_folder(u.uid, "f1", "ggg")
    await create_folder(u.uid, "f1", "f2", "f3")
    await create_folder(u.uid, "f1", "f2", "f31")
    await create_folder(u.uid, "f1", "f2", "f3", "f4")

    fs = await fetch_namespace(u.uid)
    assert fs.roots == ["f1"]
    assert fs.children("f1") == ["f2", "fff", "ggg"]
    assert fs.children("f1", "f2") == ["f3", "f31"]
    assert fs.children("f1", "f2", "f3") == ["f4"]
    assert fs.children("f1", "f2", "f3", "f4") == []
    assert fs.children("f1", "unexist") == []


@mark_async_test()
async def test_fetch_subfolders(u: LUser) -> None:
    """ネットワークを辿ってフォルダを取得."""
    f1 = await create_folder(u.uid, "f1")
    f2 = await create_folder(u.uid, "f1", "f2")
    f21 = await create_folder(u.uid, "f1", "f21")
    f3 = await create_folder(u.uid, "f1", "f2", "f3")

    ns = await fetch_namespace(u.uid)
    assert f1.frozen == ns.get("f1")
    assert f2.frozen == ns.get("f1", "f2")
    assert f21.frozen == ns.get("f1", "f21")
    assert f3.frozen == ns.get("f1", "f2", "f3")


@mark_async_test()
async def test_folder_move(u: LUser) -> None:
    """フォルダの移動(配下ごと)."""
    await create_folder(u.uid, "f1")
    await create_folder(u.uid, "f2")
    tgt = await create_folder(u.uid, "f1", "target")
    sub = await create_folder(u.uid, "f1", "target", "sub")
    await create_folder(u.uid, "f2", "other")
    ns = await fetch_namespace(u.uid)
    assert tgt.frozen == ns.get("f1", "target")
    assert sub.frozen == ns.get("f1", "target", "sub")
    await move_folder(u.uid, "/f1/target", "/f2/xxx")
    ns = await fetch_namespace(u.uid)
    assert ns.get_or_none("f1", "target") is None  # なくなってる
    assert ns.get("f2", "xxx", "sub")


@mark_async_test()
async def test_namespace_each_user(u: LUser):
    """ユーザーごとのnamespaceが取得できる."""
    # 同タイトルは登録できない.
    await create_folder(u.uid, "f1")
    await create_resource(u.uid, "r1")
    with pytest.raises(EntryAlreadyExistsError):
        await create_resource(u.uid, "f1", "r1")  # 階層が違えば同名でも登録できる
    ns = await fetch_namespace(u.uid)
    assert ns.roots == ["f1", "r1"]
    # assert ns.children("f1") == ["r1"]

    # 別のユーザーには追加されない
    u2 = await LUser(email="two@gmail.com").save()
    ns = await fetch_namespace(u.uid)
    ns2 = await fetch_namespace(u2.uid)
    assert len(ns.g.nodes) == 2  # noqa: PLR2004
    assert len(ns2.g.nodes) == 0


# def test_delete_folder(u: LUser) -> None:
#     """フォルダの削除(配下ごと)."""
#     create_folder(u.uid, "f1")
#     create_resource(u.uid, "r1")
#     create_resource(u.uid, "r2")
#     create_resource(u.uid, "f1", "r21")

#     ns = fetch_namespace(u.uid)

#     nxprint(ns.g)
