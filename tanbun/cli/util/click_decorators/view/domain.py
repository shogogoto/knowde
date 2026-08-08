"""domain."""

from __future__ import annotations

import json
from typing import Literal, TypeVar

import click
from pydantic import BaseModel
from tabulate import tabulate


class ExtraPropertyError(Exception):
    """余分なドメインモデルの属性を指定してしまった."""


T = TypeVar("T", bound=BaseModel)


def check_includes_props[T: BaseModel](t: type[T], props: set[str] | None) -> None:
    """キーがmodelに含まれていなければエラー."""
    all_props = set(t.model_fields)
    if props is None:
        props = all_props
    extra = props - all_props
    if len(extra) > 0:
        msg = (
            f"{sorted(extra)}は{t.__class__}に含まれていない属性です."
            f"{sorted(all_props)}のいずれかを指定してください"
        )
        raise ExtraPropertyError(msg)


def filter_props_json[T: BaseModel](
    models: list[T],
    props: set[str] | None,
) -> list[object]:
    """指定プロパティのJSONを抽出."""
    if len(models) == 0:
        return []
    m = models[0]
    check_includes_props(m.__class__, props)
    return [
        m.model_dump(mode="json", include=props, exclude={"created"}) for m in models
    ]


def table_view(js: list) -> str:  # noqa: D103
    return tabulate(js, headers="keys", showindex=True)


def rows_view(js: list) -> str:  # noqa: D103
    return tabulate(js, headers=(), tablefmt="plain", showindex=False)


type Style = Literal["json", "table", "rows"]


def view[T: BaseModel](  # noqa: D103
    models: list[T],
    props: set[str],
    style: Style = "table",
) -> None:
    props_ = props
    if len(props_) == 0:
        props_ = None

    js = filter_props_json(models, props_)
    if style == "json":
        txt = json.dumps(js, indent=2)
    elif style == "table":
        txt = table_view(js)
    elif style == "rows":
        txt = rows_view(js)
    click.echo(txt)
