"""timeline interface."""
import click

from knowde._feature._shared.api.api_param import APIPath, APIQuery, NullPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_apifunc, to_queryfunc
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde._feature.timeline.domain.domain import TimeValue
from knowde._feature.timeline.interface.dto import (
    TimelineAddParam,
    TimelineListRemoveParam,
)
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.remove import remove_time
from knowde._feature.timeline.repo.timeline import list_timeline

tl_router = Endpoint.Timeline.create_router()
cf = ClientFactory(router=tl_router, rettype=TimeValue)

add_client = cf.post(
    NullPath(),
    to_apifunc(fetch_time, TimelineAddParam, convert=lambda x: x.value),
    t_body=TimelineAddParam,
)
list_client = cf.gets(
    NullPath(),
    to_queryfunc(
        list_timeline,
        [str, int | None, int | None],
        list[TimeValue],
        lambda x: x.values,
    ),
    query=APIQuery(name="name").add("year").add("month"),
)
rm_client = cf.delete(
    APIPath(name="name", prefix=""),
    remove_time,
    query=APIQuery(name="name").add("year").add("month"),
)


@click.group("tl")
def tl_cli() -> None:
    """時系列."""


@tl_cli.command("add")
@model2decorator(TimelineAddParam)
def _add(**kwargs) -> None:  # noqa: ANN003
    """追加."""
    t = add_client(**kwargs)
    click.echo("以下を作成しました")
    click.echo(t)


@tl_cli.command("ls")
@model2decorator(TimelineListRemoveParam)
def _ls(**kwargs) -> None:  # noqa: ANN003
    """一覧."""
    ts = list_client(**kwargs)
    for t in ts:
        click.echo(t)


@tl_cli.command("rm")
@model2decorator(TimelineListRemoveParam)
def _rm(**kwargs) -> None:  # noqa: ANN003
    """削除."""
    rm_client(**kwargs)
    click.echo(f"{kwargs}を削除しました")
