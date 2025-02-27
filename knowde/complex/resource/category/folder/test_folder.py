"""test folder."""



import pytest

from knowde.complex.resource.category.folder.errors import (
    FolderAlreadyExistsError,
    SubFolderCreateError,
)
from knowde.complex.resource.category.folder.repo import (
    create_root_folder,
    create_sub_folder,
    fetch_root_folders,
)
from knowde.primitive.user.repo import LUser


@pytest.fixture()
def u() -> LUser:  # noqa: D103
    return LUser(email="one@gmail.com").save()


def test_create_root_folder(u: LUser) -> None:
    """User直下フォルダ."""
    f1 = create_root_folder(u.uid, "f1")
    assert [f1] == fetch_root_folders(u.uid)


def test_create_duplicated_root_folder(u: LUser) -> None:
    """User直下の重複フォルダ."""
    create_root_folder(u.uid, "f1")
    with pytest.raises(FolderAlreadyExistsError):
        create_root_folder(u.uid, "f1")


def test_create_sub_unexist_parent(u: LUser) -> None:
    """存在しない親の下にフォルダ作ろうとしちゃった."""
    with pytest.raises(SubFolderCreateError):
        create_sub_folder(u.uid, "unexist", "f2")


def test_create_sub_folder(u: LUser) -> None:
    """サブフォルダ作成."""
    f1 = create_root_folder(u.uid, "f1")
    f2 = create_sub_folder(u.uid, "f1", "f2")
    with pytest.raises(FolderAlreadyExistsError):
        create_sub_folder(u.uid, "f1", "f2")

    f3 = create_sub_folder(u.uid, "f1", "f2", "f3")
    f31 = create_sub_folder(u.uid, "f1", "f2", "f31")
    f4 = create_sub_folder(u.uid, "f1", "f2", "f3", "f4")
    with pytest.raises(SubFolderCreateError):
        create_sub_folder(u.uid, "f1", "f2", "ffff", "f4")

    assert f1.parent.all() == []
    assert f2.parent.get(name="f1") == f1  # RelationshipManagerの使い方例
    assert f3.parent.all() == f31.parent.all() == [f2]
    assert f4.parent.all() == [f3]


# def test_folder_name() -> None:
#     pass


# def test_folder_move() -> None:
#     pass
