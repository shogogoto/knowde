from knowde._feature.reference.repo.node import add_part, add_reference, find_reference


def test_create() -> None:
    add_reference("book")


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
