"""util."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def parted(it: Iterable, f: Callable[..., bool]) -> tuple[list, list]:
    """iterを条件で2分割."""
    matches = list(filter(f, it))
    not_matches = [e for e in it if e not in matches]
    return matches, not_matches
