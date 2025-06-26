"""test folder."""

import pytest

from knowde.feature.entry.errors import EntryAlreadyExistsError, EntryNotFoundError
from knowde.feature.user.repo.repo import LUser

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


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="one@gmail.com").save()


def test_create_root_folder(u: LUser) -> None:
    """User直下フォルダ."""
    create_root_folder(u.uid, "f1")
    fs = fetch_namespace(u.uid)
    assert fs.roots == ["f1"]


def test_create_duplicated_root_folder(u: LUser) -> None:
    """User直下の重複フォルダ."""
    create_root_folder(u.uid, "f1")
    create_root_folder(u.uid, "f2")
    create_sub_folder(u.uid, "f2", "f1")
    with pytest.raises(EntryAlreadyExistsError):
        create_root_folder(u.uid, "f1")


def test_create_sub_unexist_parent(u: LUser) -> None:
    """存在しない親の下にフォルダ作ろうとしちゃった."""
    with pytest.raises(EntryNotFoundError):
        create_sub_folder(u.uid, "unexist", "f2")


def test_create_duplicated_sub_folder(u: LUser) -> None:
    """同じ親に対してサブフォルダを複数作る."""
    create_root_folder(u.uid, "f1")
    create_sub_folder(u.uid, "f1", "f2")
    with pytest.raises(EntryAlreadyExistsError):
        create_sub_folder(u.uid, "f1", "f2")


@pytest.mark.skip
def test_fetch_folderspace(u: LUser) -> None:
    """ユーザー配下のフォルダ空間を一括取得."""
    create_root_folder(u.uid, "f1")
    create_sub_folder(u.uid, "f1", "f2")
    create_sub_folder(u.uid, "f1", "fff")
    create_sub_folder(u.uid, "f1", "ggg")
    create_sub_folder(u.uid, "f1", "f2", "f3")
    create_sub_folder(u.uid, "f1", "f2", "f31")
    create_sub_folder(u.uid, "f1", "f2", "f3", "f4")

    fs = fetch_namespace(u.uid)
    assert fs.roots == ["f1"]
    assert fs.children("f1") == ["f2", "fff", "ggg"]
    assert fs.children("f1", "f2") == ["f3", "f31"]
    assert fs.children("f1", "f2", "f3") == ["f4"]
    assert fs.children("f1", "f2", "f3", "f4") == []
    assert fs.children("f1", "unexist") == []


def test_fetch_subfolders(u: LUser) -> None:
    """ネットワークを辿ってフォルダを取得."""
    f1 = create_folder(u.uid, "f1")
    f2 = create_folder(u.uid, "f1", "f2")
    f21 = create_folder(u.uid, "f1", "f21")
    f3 = create_folder(u.uid, "f1", "f2", "f3")
    assert f1 == fetch_subfolders(u.uid, "f1")[0]
    assert f2 == fetch_subfolders(u.uid, "f1", "f2")[0]
    assert f21 == fetch_subfolders(u.uid, "f1", "f21")[0]
    assert f3 == fetch_subfolders(u.uid, "f1", "f2", "f3")[0]


def test_folder_move(u: LUser) -> None:
    """フォルダの移動(配下ごと)."""
    create_folder(u.uid, "f1")
    create_folder(u.uid, "f2")
    create_folder(u.uid, "f1", "target")
    create_folder(u.uid, "f1", "target", "sub")
    create_folder(u.uid, "f2", "other")
    tgt, subs = fetch_subfolders(u.uid, "f1", "target")
    assert tgt.name == "target"
    assert [s.name for s in subs] == ["sub"]
    move_folder(u.uid, "/f1/target", "/f2/xxx")
    ns = fetch_namespace(u.uid)
    assert ns.get_or_none("f1", "target") is None  # なくなってる
    assert ns.get("f2", "xxx", "sub")


def test_create_resource(u: LUser) -> None:
    """フォルダ(composite)とファイル(leaf)を両方扱えるように拡張."""
    create_folder(u.uid, "f1")
    create_root_resource(u.uid, "r1")
    create_sub_resource(u.uid, "f1", "r1")  # 階層が違えば同名でも登録できる
    # -> 登録できないように変更
    ns = fetch_namespace(u.uid)
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
