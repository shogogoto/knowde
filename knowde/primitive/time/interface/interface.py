"""timeline interface."""
import click

from knowde.core.api.api_param import APIPath, APIQuery, NullPath
from knowde.core.api.endpoint import Endpoint
from knowde.core.api.facade import ClientFactory
from knowde.core.api.paramfunc import to_bodyfunc, to_queryfunc
from knowde.core.cli.field.model2click import model2decorator
from knowde.primitive.time.domain.domain import TimeValue
from knowde.primitive.time.domain.timestr import TimeStr
from knowde.primitive.time.interface.dto import (
    TimelineParam,
    TimeStrParam,
)
from knowde.primitive.time.repo.fetch import fetch_time
from knowde.primitive.time.repo.remove import remove_time
from knowde.primitive.time.repo.timeline import list_time

tl_router = Endpoint.Timeline.create_router()
cf = ClientFactory(router=tl_router, rettype=TimeValue)

add_client = cf.post(
    NullPath(),
    to_bodyfunc(fetch_time, TimelineParam, convert=lambda x: x.value),
    t_body=TimelineParam,
)
list_client = cf.gets(
    NullPath(),
    to_queryfunc(
        list_time,
        [str, int | None, int | None],
        list[TimeValue],
    ),
    query=APIQuery(name="name").add("year").add("month"),
)
rm_client = cf.delete(
    APIPath(name="name", prefix=""),
    to_bodyfunc(remove_time, TimelineParam),
    t_body=TimelineParam,
)


@click.group("time")
def tl_cli() -> None:
    """時系列.

    時刻文字列(timestr) e.g. yyyy/MM/dd@name, yyyy, yyyy/MM, @name
    """


@tl_cli.command("add")
@model2decorator(TimeStrParam)
def _add(timestr: str) -> None:
    """追加."""
    ts = TimeStr(value=timestr)
    t = add_client(**ts.val.model_dump())
    click.echo("以下を作成しました")
    click.echo(t)


@tl_cli.command("ls")
@model2decorator(TimeStrParam)
def _ls(timestr: str) -> None:
    """一覧."""
    s = TimeStr(value=timestr)
    ls = list_client(**s.val.model_dump())
    for t in sorted(ls):
        click.echo(t)


@tl_cli.command("rm")
@model2decorator(TimeStrParam)
def _rm(timestr: str) -> None:
    """削除."""
    s = TimeStr(value=timestr)
    rm_client(**s.val.model_dump())
    click.echo(f"{timestr}を削除しました")
