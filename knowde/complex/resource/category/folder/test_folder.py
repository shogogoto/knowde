"""test folder."""
import pytest

from knowde.primitive.user.repo import LUser

from .errors import (
    FolderAlreadyExistsError,
    SubFolderCreateError,
)
from .repo import (
    create_root_folder,
    create_sub_folder,
    fetch_folders,
    fetch_root_folders,
)


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


def test_create_sub_folders() -> None:
    """同じ親に対してサブフォルダを複数作る."""


def test_create_sub_folder(u: LUser) -> None:
    """サブフォルダ作成."""
    create_root_folder(u.uid, "f1")
    create_sub_folder(u.uid, "f1", "f2")
    with pytest.raises(FolderAlreadyExistsError):
        create_sub_folder(u.uid, "f1", "f2")

    create_sub_folder(u.uid, "f1", "f2", "f3")
    create_sub_folder(u.uid, "f1", "f2", "f31")
    create_sub_folder(u.uid, "f1", "f2", "f3", "f4")
    with pytest.raises(SubFolderCreateError):
        create_sub_folder(u.uid, "f1", "f2", "ffff", "f4")

    fs = fetch_folders(u.uid)
    assert fs.roots == ["f1"]
    assert fs.children("f1") == ["f2"]
    assert fs.children("f1", "f2") == ["f3", "f31"]
    assert fs.children("f1", "f2", "f3") == ["f4"]
    assert fs.children("f1", "f2", "f3", "f4") == []
    assert fs.children("f1", "unexist") == []


# def test_folder_name() -> None:
#     pass


# def test_folder_move() -> None:
#     pass
