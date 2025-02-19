"""models for presentation layer."""
from __future__ import annotations

from textwrap import indent

import click
from pydantic import BaseModel, Field

from knowde.primitive.__core__.domain import APIReturn, Composite
from knowde.tmp.definition.domain.domain import Definition  # noqa: TCH001


def view_detail(composite: Composite[Definition]) -> str:
    """複数行のテキスト表現."""
    txt = composite.parent.output
    for c in composite.children:
        txt += "\n" + indent(view_detail(c), " " * 2)
    return txt


class DetailParam(BaseModel, frozen=True):
    """term uuid param for api."""

    pref_def_uid: str = Field(description="用語のuuidへ前方一致")


class DetailView(APIReturn, frozen=True):
    """show definition composite."""

    detail: Composite[Definition] | None = None

    def echo(self) -> None:
        """Print for cli."""
        if self.detail is None:
            click.echo("not detail")
        else:
            click.echo(view_detail(self.detail))
