from knowde._feature._shared.domain import ModelList
from knowde._feature.reference.repo.node import (
    add_author,
    add_part,
    add_root,
    find_reference,
    find_roots,
)

from .label import author_util


def test_add_root() -> None:
    assert len(find_roots()) == 0
    ref1 = add_root("book")
    add_root("book2")
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
    ref1 = add_root("book1")
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


def test_add_author() -> None:
    ref = add_root("with_author")
    author = add_author("oresama", ref)
    assert author == author_util.find_one(author.valid_uid).to_model()
    roots = find_roots()
    assert roots[0].authors == {author}
    assert len(roots) == 1

    author2 = add_author("oremo", ref)
    roots = find_roots()
    assert roots[0].authors == {author, author2}
    assert len(roots) == 1
