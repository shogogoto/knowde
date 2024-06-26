from __future__ import annotations

from inspect import signature

import pytest

from .func import VariadicArgumentsUndefinedError, rename_argument


def test_rename_argument() -> None:
    """Valid case."""

    def func(
        a: str,
        b: int,
        *args,  # noqa: ARG001, ANN002
        **kwargs,  # noqa: ARG001, ANN003
    ) -> tuple[str, int]:
        return a, b

    func2 = rename_argument("a", "replaced")(func)
    arg1, arg2 = "xyz", 1
    assert "replaced" not in str(signature(func))
    assert func(arg1, arg2) == func2(arg1, arg2)
    assert "replaced" in str(signature(func2))


def test_invalid_rename_argument() -> None:
    """Invalid case."""
    with pytest.raises(VariadicArgumentsUndefinedError):

        @rename_argument("a", "replaced")
        def func(a: str, b: int) -> tuple[str, int]:
            # def func(a: str, b: int) -> tuple[str, int]:
            return a, b
