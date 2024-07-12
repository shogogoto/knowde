from pytest_unordered import unordered

from knowde._feature.location.repo.repo import (
    add_location_root,
    add_sub_location,
    find_location_tree,
)


def test_sub_location() -> None:
    root = add_location_root("JP")
    s1 = add_sub_location(root.valid_uid, "Tokyo")
    s2 = add_sub_location(root.valid_uid, "Osaka")

    tree = find_location_tree(root.valid_uid)
    assert tree.parent == root
    assert tree.get_children() == unordered([s1, s2])
