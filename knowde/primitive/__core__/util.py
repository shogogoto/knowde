"""util."""
from __future__ import annotations

from itertools import filterfalse
from typing import Callable


def parted(it: iter, f: Callable[..., bool]) -> tuple[list, list]:
    """iterを条件で2分割."""
    return list(filter(f, it)), list(filterfalse(f, it))
