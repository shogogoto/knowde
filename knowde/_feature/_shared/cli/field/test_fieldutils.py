from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model

from .fieldutils import extract_type, is_nested, is_option


class NestedModel(BaseModel):
    dummy: int


class OneModel(BaseModel):
    pstr: str
    pstr_: str | None
    pstr__: Optional[str]
    pex: str = Field(exclude=True)
    nested: NestedModel
    nested_: NestedModel | None


OneModelPartial = create_partial_model(OneModel)


def test_is_nested() -> None:
    assert not is_nested(OneModel.model_fields["pstr"].annotation)
    assert not is_nested(OneModel.model_fields["pstr_"].annotation)
    assert not is_nested(OneModel.model_fields["pstr__"].annotation)
    assert is_nested(OneModel.model_fields["nested"].annotation)
    assert is_nested(OneModel.model_fields["nested_"].annotation)


def test_option() -> None:
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


def test_extract_type() -> None:
    assert extract_type(str) == str
    assert extract_type(str | None) == str
    assert extract_type(Optional[str]) == str
    assert extract_type(Optional[OneModel]) == OneModel
