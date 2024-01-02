from __future__ import annotations

from typing import TYPE_CHECKING

import click
from click.testing import CliRunner

from knowde._feature._shared.api.param import ApiParam

from .to_wrapper import to_click_wrappers

if TYPE_CHECKING:
    from click import Argument


class OneParam(ApiParam, frozen=True):
    p1: str


def test_to_arg_wrapper() -> None:
    wrap = to_click_wrappers(OneParam(p1="x"))[0]

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
    wrap = to_click_wrappers(AParam(p2=0))[0]

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
    ws = to_click_wrappers(MultiParam(p3=0, p4="p4"))

    @click.command()
    @ws.wraps
    def _dummy(p3: int | None, p4: str) -> None:
        if p3 is not None:
            click.echo(f"p3={p3}")
        click.echo(f"p4={p4}")

    runner = CliRunner()
    result = runner.invoke(_dummy, ["p4-arg"])
    assert "p3" not in result.output
    assert "p4" in result.output

    result = runner.invoke(_dummy, ["dummy", "--p3", "999"])
    assert "p3" in result.output
    assert "999" in result.output
