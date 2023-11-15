"""repository test."""


from knowde.feature.concept.repo import list_concepts


def test_list() -> None:
    """Temp."""
    ls = list_concepts()
    print(ls)  # noqa: T201
