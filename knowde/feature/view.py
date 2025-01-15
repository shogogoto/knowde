"""load-file."""
from __future__ import annotations

from typing import IO

import click
from tabulate import tabulate

from knowde.complex.systats.nw1_n0 import Systats, UnificationRatio
from knowde.complex.systats.nw1_n0.syscontext import (
    RecWeight,
    SysContext,
    SysContexts,
    SysCtxItem,
)
from knowde.feature.__core__ import try_parse2net

"""
TODO:
    # 表示項目の変更
    #     default
    #     Choice
    #     ignore
    重みつき
    sort
        数値として
        文字列として
    recursive n指定
"""


ItemT = click.Choice(tuple(SysCtxItem))


@click.command("view")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option("-n", "--number", type=click.INT, default=15, help="表示行数数")
@click.option(
    "-i",
    "--item",
    type=ItemT,
    multiple=True,
    default=tuple(SysCtxItem),
    show_default=True,
    help="表示項目",
)
@click.option(
    "-ig",
    "--ignore",
    type=ItemT,
    multiple=True,
    help="非表示項目",
    show_default=True,
)
@click.option(
    "-c",
    "--config",
    type=click.Tuple([SysCtxItem, click.INT, click.INT]),
    multiple=True,
    help="(項目,再帰回数,重み)",
)
def view_cmd(
    stdin: IO,
    number: int,
    item: tuple[SysCtxItem],
    ignore: tuple[SysCtxItem],
    config: tuple[RecWeight],
) -> None:
    """重要度でソート."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    # sn = parse2net(txt)
    stats = Systats.to_dict(sn) | UnificationRatio.to_dictstr(sn)
    click.echo(tabulate([stats], headers="keys"))
    items = [SysContext.from_item(i) for i in item if i not in ignore]
    ctx = SysContexts(values=items, num=number, configs=list(config))
    click.echo(ctx.table(sn))


# typerのがいいかどうか... file inputの補完が効かないからclickを使うままにしておく
# def view_vcmd(
#     # stdin: Annotated[typer.FileText, typer.Argument(mode="r")] = sys.stdin,
#     p: Annotated[Path, typer.Argument(mode="r")],
# ) -> None:
#     txt = p.read_text()
#     # sn = try_parse2net(txt)jk
#     sn = parse2net(txt)
#     nxprint(sn.g)


# @click.command("parse")
# @click.argument("stdin", type=click.File("r"), default="-")
# def parse_cmd(stdin: IO) -> None:
#     """入力テキストのパース."""
#     txt = stdin.read()
#     _sn = try_parse2net(txt)
#     js = nx2json_dump(_sn.g)
#     print(js)
