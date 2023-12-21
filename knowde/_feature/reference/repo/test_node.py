from pytest_unordered import unordered

from knowde._feature._shared.domain import ModelList
from knowde._feature.reference.repo.node import (
    add_author,
    add_part,
    add_root,
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

    actual = ModelList(root=find_roots().roots).model_dump(
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

    g_root = find_roots()
    tree = g_root.tree(ref1, include={"name"})
    expected = {
        "name": "book1",
        "children": unordered(
            {
                "name": "part1",
                "children": unordered(
                    {"name": "part11"},
                    {"name": "part12"},
                ),
            },
            {"name": "part2"},
        ),
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
    g_roots = find_roots()
    root = ModelList(root=list(g_roots.G.nodes)).first("name", "with_author")

    assert g_roots.tree(root).authors == (author,)
    assert len(g_roots) == 1

    author2 = add_author("oremo", ref)
    g_roots = find_roots()
    root = ModelList(root=list(g_roots.G.nodes)).first("name", "with_author")
    assert g_roots.tree(root).authors == (author, author2)
    assert len(g_roots) == 2  # noqa: PLR2004
