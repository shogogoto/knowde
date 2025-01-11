"""util."""
from __future__ import annotations

from typing import Callable


def parted(it: iter, f: Callable[..., bool]) -> tuple[list, list]:
    """iterを条件で2分割."""
    matches = list(filter(f, it))
    not_matches = [e for e in it if e not in matches]
    return matches, not_matches
