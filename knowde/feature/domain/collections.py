"""コレクションに関する共通操作."""

from collections.abc import Callable, Iterable


def parted(it: Iterable, f: Callable[..., bool]) -> tuple[list, list]:
    """Iterableを条件で2分割する."""
    matches = list(filter(f, it))
    not_matches = [element for element in it if element not in matches]
    return matches, not_matches
