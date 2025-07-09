"""test folder."""

from collections.abc import AsyncGenerator

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.errors import EntryAlreadyExistsError, EntryNotFoundError
from knowde.shared.labels.user import LUser

from .repo import (
    create_folder,
    create_root_folder,
    create_root_resource,
    create_sub_folder,
    create_sub_resource,
    fetch_namespace,
    fetch_subfolders,
    move_folder,
)


@async_fixture()
async def u() -> AsyncGenerator[LUser, None]:  # noqa: D103
    return await LUser(email="one@gmail.com").save()


@mark_async_test()
async def test_create_root_folder(u: LUser) -> None:
    """User直下フォルダ."""
    await create_root_folder(u.uid, "f1")
    fs = await fetch_namespace(u.uid)
    assert fs.roots == ["f1"]


@mark_async_test()
async def test_create_duplicated_root_folder(u: LUser) -> None:
    """User直下の重複フォルダ."""
    await create_root_folder(u.uid, "f1")
    await create_root_folder(u.uid, "f2")
    await create_sub_folder(u.uid, "f2", "f1")
    with pytest.raises(EntryAlreadyExistsError):
        await create_root_folder(u.uid, "f1")


@mark_async_test()
async def test_create_sub_unexist_parent(u: LUser) -> None:
    """存在しない親の下にフォルダ作ろうとしちゃった."""
    with pytest.raises(EntryNotFoundError):
        await create_sub_folder(u.uid, "unexist", "f2")


@mark_async_test()
async def test_create_duplicated_sub_folder(u: LUser) -> None:
    """同じ親に対してサブフォルダを複数作る."""
    await create_root_folder(u.uid, "f1")
    await create_sub_folder(u.uid, "f1", "f2")
    with pytest.raises(EntryAlreadyExistsError):
        await create_sub_folder(u.uid, "f1", "f2")


@mark_async_test()
async def test_fetch_folderspace(u: LUser) -> None:
    """ユーザー配下のフォルダ空間を一括取得."""
    await create_root_folder(u.uid, "f1")
    await create_sub_folder(u.uid, "f1", "f2")
    await create_sub_folder(u.uid, "f1", "fff")
    await create_sub_folder(u.uid, "f1", "ggg")
    await create_sub_folder(u.uid, "f1", "f2", "f3")
    await create_sub_folder(u.uid, "f1", "f2", "f31")
    await create_sub_folder(u.uid, "f1", "f2", "f3", "f4")

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

    f1_ = await fetch_subfolders(u.uid, "f1")
    assert f1 == f1_[0]
    f2_ = await fetch_subfolders(u.uid, "f1", "f2")
    assert f2 == f2_[0]
    f21_ = await fetch_subfolders(u.uid, "f1", "f21")
    assert f21 == f21_[0]
    f3_ = await fetch_subfolders(u.uid, "f1", "f2", "f3")
    assert f3 == f3_[0]


@mark_async_test()
async def test_folder_move(u: LUser) -> None:
    """フォルダの移動(配下ごと)."""
    await create_folder(u.uid, "f1")
    await create_folder(u.uid, "f2")
    await create_folder(u.uid, "f1", "target")
    await create_folder(u.uid, "f1", "target", "sub")
    await create_folder(u.uid, "f2", "other")
    tgt, subs = await fetch_subfolders(u.uid, "f1", "target")
    assert tgt.name == "target"
    assert [s.name for s in subs] == ["sub"]
    await move_folder(u.uid, "/f1/target", "/f2/xxx")
    ns = await fetch_namespace(u.uid)
    assert ns.get_or_none("f1", "target") is None  # なくなってる
    assert ns.get("f2", "xxx", "sub")


@mark_async_test()
async def test_create_resource(u: LUser) -> None:
    """フォルダ(composite)とファイル(leaf)を両方扱えるように拡張."""
    await create_folder(u.uid, "f1")
    await create_root_resource(u.uid, "r1")
    await create_sub_resource(u.uid, "f1", "r1")  # 階層が違えば同名でも登録できる
    # -> 登録できないように変更
    ns = await fetch_namespace(u.uid)
    assert ns.roots == ["f1", "r1"]
    assert ns.children("f1") == ["r1"]


# def test_delete_folder(u: LUser) -> None:
#     """フォルダの削除(配下ごと)."""
#     create_folder(u.uid, "f1")
#     create_resource(u.uid, "r1")
#     create_resource(u.uid, "r2")
#     create_resource(u.uid, "f1", "r21")

#     ns = fetch_namespace(u.uid)

#     nxprint(ns.g)
