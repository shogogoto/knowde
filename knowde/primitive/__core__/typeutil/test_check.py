"""test."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model

from .check import is_generic_alias, is_nested, is_option


class NestedModel(BaseModel):  # noqa: D101
    dummy: int


class OneModel(BaseModel):  # noqa: D101
    pstr: str
    pstr_: str | None
    pstr__: str | None
    pex: str = Field(exclude=True)
    nested: NestedModel
    nested_: NestedModel | None
    uid: UUID
    uids: list[UUID]


OneModelPartial = create_partial_model(OneModel)


def test_is_nested() -> None:  # noqa: D103
    assert not is_nested(OneModel.model_fields["pstr"].annotation)
    assert not is_nested(OneModel.model_fields["pstr_"].annotation)
    assert not is_nested(OneModel.model_fields["pstr__"].annotation)
    assert is_nested(OneModel.model_fields["nested"].annotation)
    assert is_nested(OneModel.model_fields["nested_"].annotation)


def test_option() -> None:  # noqa: D103
    assert not is_option(OneModel.model_fields["pstr"].annotation)
    assert is_option(OneModel.model_fields["pstr_"].annotation)
    assert is_option(OneModel.model_fields["pstr__"].annotation)
    assert not is_option(OneModel.model_fields["nested"].annotation)
    assert not is_option(OneModel.model_fields["nested_"].annotation)

    assert is_option(OneModelPartial.model_fields["pstr"].annotation)
    assert is_option(OneModelPartial.model_fields["pstr_"].annotation)
    assert is_option(OneModelPartial.model_fields["pstr__"].annotation)
    assert not is_option(OneModelPartial.model_fields["nested"].annotation)
    assert not is_option(OneModel.model_fields["nested_"].annotation)


def test_alias_type() -> None:  # noqa: D103
    assert not is_generic_alias(OneModel.model_fields["uid"].annotation)
    assert is_generic_alias(OneModel.model_fields["uids"].annotation)
