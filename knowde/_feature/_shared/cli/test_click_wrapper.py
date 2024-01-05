from __future__ import annotations

from typing import TYPE_CHECKING

import click
from click.testing import CliRunner
from pydantic import BaseModel, Field

from knowde._feature._shared.api.param import ApiParam

from .click_wrapper import to_click_wrappers

if TYPE_CHECKING:
    from click import Argument


class OneParam(ApiParam, frozen=True):
    p1: str


def test_to_arg_wrapper() -> None:
    wrap = to_click_wrappers(OneParam)[0]

    @wrap
    def _dummy() -> None:
        pass

    p: Argument = _dummy.__click_params__[0]
    assert p.name == "p1"
    assert p.nargs == 1
    assert p.type == click.STRING
    assert p.param_type_name == "argument"


class AParam(ApiParam, frozen=True):
    p2: int | None = None


def test_to_option_wrapper() -> None:
    wrap = to_click_wrappers(AParam)[0]

    @wrap
    def _dummy() -> None:
        pass

    p: click.Option = _dummy.__click_params__[0]
    assert p.name == "p2"
    assert p.type == click.INT
    assert p.param_type_name == "option"


class MultiParam(ApiParam, frozen=True):
    p3: int | None = None
    p4: str


def test_multi_parameters() -> None:
    ws = to_click_wrappers(MultiParam)

    @click.command()
    @ws.wraps
    def _dummy(p3: int | None, p4: str) -> None:
        click.echo(f"{p3}{p4}")

    runner = CliRunner()
    result = runner.invoke(_dummy, ["p4"])
    assert result.output.strip() == "Nonep4"

    result = runner.invoke(_dummy, ["dummy", "--p3", "999"])
    assert result.output.strip() == "999dummy"


class DescParam(ApiParam, frozen=True):
    p: str | None = Field(None, description="description_test")


def test_description() -> None:
    ws = to_click_wrappers(DescParam)

    @click.command()
    @ws.wraps
    def _dummy(p: str | None) -> None:  # noqa: ARG001
        pass

    runner = CliRunner()
    result = runner.invoke(_dummy, "--help")
    assert "description_test" in result.output


class ChildModel(BaseModel, frozen=True):
    n1: int
    n2: str | None


class ParentModel(ApiParam, frozen=True):
    p: bool
    nested: ChildModel


def test_nested_model() -> None:
    @click.command()
    @to_click_wrappers(ParentModel).wraps
    def _dummy(p: bool, n1: int, n2: str | None) -> None:  # noqa: FBT001
        click.echo(f"{p}{n1}{n2}")

    # 逆順で並ぶ
    ps = _dummy.params
    assert ps[0].name == "p"
    assert ps[0].param_type_name == "argument"
    assert ps[1].name == "n1"
    assert ps[1].param_type_name == "argument"
    assert ps[2].name == "n2"
    assert ps[2].param_type_name == "option"

    runner = CliRunner()
    result = runner.invoke(_dummy, ["True", "0", "--n2", "n2"])
    assert result.output.strip() == "True0n2"
