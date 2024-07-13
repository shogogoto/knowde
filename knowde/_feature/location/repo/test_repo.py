from pytest_unordered import unordered

from knowde._feature.location.repo.repo import (
    add_location_root,
    add_sub_location,
    find_location_tree,
    remove_location,
)


def test_location_tree_crud() -> None:
    root = add_location_root("JP")
    s1 = add_sub_location(root.valid_uid, "Tokyo")
    s2 = add_sub_location(root.valid_uid, "Osaka")
    tree = find_location_tree(root.valid_uid)
    assert tree.root == root
    assert tree.children(root) == unordered([s1, s2])
    assert tree.children(s1) == []
    assert tree.children(s2) == []

    s11 = add_sub_location(s1.valid_uid, "Shinagawa")
    s12 = add_sub_location(s1.valid_uid, "Mitaka")
    s21 = add_sub_location(s2.valid_uid, "Nanba")
    tree2 = find_location_tree(root.valid_uid)
    assert tree2.root == root
    assert tree2.children(root) == unordered([s1, s2])
    assert tree2.children(s1) == unordered([s11, s12])
    assert tree2.children(s2) == [s21]

    remove_location(s1.valid_uid)
    tree3 = find_location_tree(root.valid_uid)
    assert tree3.root == root
    assert tree3.children(root) == [s2]
    assert tree3.children(s1) == []
    assert tree3.children(s2) == [s21]
