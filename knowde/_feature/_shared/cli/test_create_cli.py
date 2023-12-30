from __future__ import annotations

from typing import TYPE_CHECKING

import click

from knowde._feature._shared.api.param import ApiParam
from knowde._feature._shared.cli.create_cli import to_click_wrapper

if TYPE_CHECKING:
    from click import Argument


class OneParam(ApiParam, frozen=True):
    p1: str


def test_to_arg_wrapper() -> None:
    wrap = to_click_wrapper(OneParam(p1="x"))[0]

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
    wrap = to_click_wrapper(AParam(p2=0))[0]

    @wrap
    def _dummy() -> None:
        pass

    p: click.Option = _dummy.__click_params__[0]
    assert p.name == "p2"
    assert p.type == click.INT
    assert p.param_type_name == "option"
