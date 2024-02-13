"""inspect.Parameterからclick decoratorへ変換.

fparam :: inspect.Parameter = 関数のパラメータ
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import click
from pydantic import BaseModel, Field
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.integrated_interface.generate_req import inject_signature

from .func2click import func2clickparams

if TYPE_CHECKING:
    from knowde._feature._shared.cli.to_click import ClickParam


class Nest(BaseModel):
    p: str


def to_param(f: ClickParam) -> click.Parameter:
    @f
    def _dummy() -> None:
        pass

    return _dummy.__click_params__[0]


def to_info(cp: click.Parameter) -> tuple[click.ParamType, str]:
    """確認用."""
    return cp.type, cp.param_type_name


def test_get_fparams() -> None:
    """BaseModel以外のタイプをclickparamへ変換する.

    - to argument
    - to option
    """
    NestOp = create_partial_model(Nest)  # noqa: N806

    def f(
        uid: UUID,  # noqa: ARG001
        _uid: UUID | None = None,
        __uid: Optional[UUID] = None,
        field: UUID | None = Field(description="help"),  # noqa: ARG001
        nest: Nest = Field(),  # noqa: ARG001
        _nest: NestOp = Field(),
    ) -> None:
        pass

    params = func2clickparams(
        inject_signature(  # これがないと型喪失する
            f,
            t_in=[
                UUID,
                UUID | None,
                Optional[UUID],
                UUID | None,
                Nest,
                NestOp,
            ],
        ),
    )
    cps = [to_param(p) for p in params]
    assert to_info(cps[0]) == (click.UUID, "argument")
    assert to_info(cps[1]) == (click.UUID, "option")
    assert to_info(cps[2]) == (click.UUID, "option")
    assert to_info(cps[3]) == (click.UUID, "option")
    assert cps[3].help == "help"
    assert to_info(cps[4]) == (click.STRING, "argument")
    assert to_info(cps[5]) == (click.STRING, "option")
