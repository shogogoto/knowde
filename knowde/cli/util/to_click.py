"""良う分からん、ファイル名よくなさそう."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any
from uuid import UUID

import click
from click import Context, Parameter, ParamType
from click.decorators import FC
from pydantic import BaseModel

from knowde.cli.util.typeutil.check import is_generic_alias
from knowde.cli.util.typeutil.operate import extract_generic_alias_type
from knowde.shared.timeutil import TZ


class DateType(ParamType):
    """clickでは日付をデフォルトで扱ってなかった."""

    name = "date"
    _format = "%Y-%m-%d"

    def _try_to_convert(self, value: Any) -> date | None:
        try:
            return datetime.strptime(value, self._format).astimezone(TZ).date()
        except ValueError:
            return None

    def convert(
        self,
        value: Any,
        param: Parameter | None,
        ctx: Context | None,
    ) -> date:
        """ParamTypeの実装."""
        if isinstance(value, date):
            return value
        c = self._try_to_convert(value)
        if c is not None:
            return c
        self.fail(
            f"{value} does not match the format {self._format}.",
            param,
            ctx,
        )
        return None


def to_clicktype(t: type) -> ParamType:
    """feature.parsing.primitive.typeからclickの矯正型へ."""
    if is_generic_alias(t):
        t = extract_generic_alias_type(t)
    t_map: dict[type, ParamType] = {
        str: click.STRING,
        float: click.FLOAT,
        UUID: click.UUID,
        bool: click.BOOL,
        int: click.INT,
        date: DateType(),
        datetime: click.types.DateTime(),
    }
    if t not in t_map:
        msg = f"{t} is not compatible type"
        raise TypeError(msg)
    return t_map[t]


type ClickParam = Callable[[FC], FC]


def click_decorate(params: list[ClickParam]) -> ClickParam:  # noqa: D103
    def _deco(f: FC) -> FC:
        f_ = f
        for p in reversed(params):
            f_ = p(f_)
        return f_

    return _deco


class ClickDecorator(BaseModel, frozen=True):
    """click parameter変換wrapper."""

    params: list[ClickParam]

    def __call__(self, f: FC) -> FC:
        """Implimentation."""
        return click_decorate(self.params)(f)
