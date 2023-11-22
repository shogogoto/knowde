from __future__ import annotations

import pytest
from pydantic import BaseModel

from .domain import ExtraPropertyError, check_includes_props, filter_props_json


class OneModel(BaseModel, frozen=True):
    p1: str
    p2: str | None = None


def test_check_includes_props() -> None:
    """Test."""
    m1 = OneModel(p1="p1", p2="p2")
    check_includes_props(type(m1), None)
    check_includes_props(type(m1), set())
    check_includes_props(type(m1), {"p1"})
    check_includes_props(type(m1), {"p1", "p2"})
    with pytest.raises(ExtraPropertyError):
        check_includes_props(type(m1), {"p1", "p2", "p3"})

    with pytest.raises(ExtraPropertyError):
        check_includes_props(type(m1), {"p0"})


models = [OneModel(p1=str(i), p2=str(i)) for i in range(3)]


def test_filter_props_json() -> None:
    """Test."""
    assert filter_props_json(models, {"p1"}) == [
        {"p1": "0"},
        {"p1": "1"},
        {"p1": "2"},
    ]

    with pytest.raises(ExtraPropertyError):
        filter_props_json(models, {"p3"})
