"""良う分からん、ファイル名よくなさそう."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Optional, TypeAlias
from uuid import UUID

import click
from click import Context, Parameter, ParamType
from click.decorators import FC
from pydantic import BaseModel

from knowde.primitive.__core__.timeutil import TZ
from knowde.primitive.__core__.typeutil.check import is_generic_alias
from knowde.primitive.__core__.typeutil.operate import extract_generic_alias_type


class DateType(ParamType):
    """clickでは日付をデフォルトで扱ってなかった."""

    name = "date"
    _format = "%Y-%m-%d"

    def _try_to_convert(self, value: Any) -> Optional[date]:  # noqa: ANN401
        try:
            return datetime.strptime(value, self._format).astimezone(TZ).date()
        except ValueError:
            return None

    def convert(
        self,
        value: Any,  # noqa: ANN401
        param: Optional[Parameter],
        ctx: Optional[Context],
    ) -> date:
        """ParamTypeの実装."""
        if isinstance(value, date):
            return value
        c = self._try_to_convert(value)
        if c is not None:
            return c
        self.fail(  # noqa: RET503
            f"{value} does not match the format {self._format}.",
            param,
            ctx,
        )


def to_clicktype(t: type) -> ParamType:
    """Primitive typeからclickの矯正型へ."""
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


ClickParam: TypeAlias = Callable[[FC], FC]


def click_decorate(params: list[ClickParam]) -> ClickParam:  # noqa: D103
    def _deco(f: FC) -> FC:
        _f = f
        for p in reversed(params):
            _f = p(_f)
        return _f

    return _deco


class ClickDecorator(BaseModel, frozen=True):
    """click parameter変換wrapper."""

    params: list[ClickParam]

    def __call__(self, f: FC) -> FC:
        """implimentation."""
        return click_decorate(self.params)(f)
