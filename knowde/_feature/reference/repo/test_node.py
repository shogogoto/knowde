from knowde._feature._shared.domain import ModelList
from knowde._feature.reference.repo.node import (
    add_part,
    add_reference,
    find_reference,
    find_roots,
)


def test_create() -> None:
    assert len(find_roots()) == 0
    ref1 = add_reference("book")
    add_reference("book2")
    assert len(find_roots()) == 2  # noqa: PLR2004
    add_part(ref1.valid_uid, name="part")
    # not increase root num when adding part
    assert len(find_roots()) == 2  # noqa: PLR2004

    actual = ModelList(root=find_roots()).model_dump(
        include={"__all__": {"name": ...}},
        mode="json",
    )
    assert {d["name"] for d in actual} == {"book", "book2"}


def test_add_part() -> None:
    ref1 = add_reference("book1")
    p1 = add_part(ref1.valid_uid, name="part1")
    add_part(ref1.valid_uid, name="part2")
    add_part(p1.valid_uid, name="part11")
    add_part(p1.valid_uid, name="part12")

    root = find_reference(ref1.valid_uid)
    tree = root.tree(include={"name"})
    expected = {
        "name": "book1",
        "children": [
            {
                "name": "part1",
                "children": [
                    {"name": "part11"},
                    {"name": "part12"},
                ],
            },
            {"name": "part2"},
        ],
    }
    actual = tree.model_dump(
        exclude_unset=True,
        mode="json",
    )
    assert actual == expected
