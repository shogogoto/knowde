"""load-file."""
from __future__ import annotations

import json
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
from knowde.feature.__core__.cliutil import CLIUtil

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


@click.command("stat")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option("--table/--json", default=True)
def stat_cmd(
    stdin: IO,
    table: bool,  # noqa: FBT001
) -> None:
    """統計値."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    stat = Systats.to_dict(sn) | UnificationRatio.to_dictstr(sn)
    if table:
        click.echo(tabulate([stat], headers="keys"))
    else:
        click.echo(json.dumps(stat, indent=2))


@click.command("score")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option(
    "-n",
    "--number",
    type=click.INT,
    default=15,
    help="表示行数数",
    show_default=True,
)
@CLIUtil.item_option()
@CLIUtil.ignore_option()
@click.option(
    "-c",
    "--config",
    type=click.Tuple([SysCtxItem, click.INT, click.INT]),
    multiple=True,
    help="(項目,再帰回数,重み)",
)
def score_cmd(
    stdin: IO,
    number: int,
    item: tuple[SysCtxItem],
    ignore: tuple[SysCtxItem],
    config: tuple[RecWeight],
) -> None:
    """スコアでソート."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    items = [SysContext.from_item(i) for i in item if i not in ignore]
    ctx = SysContexts(values=items, num=number, configs=list(config))
    click.echo(ctx.table(sn))


@click.command("detail")
@click.option("--stdin", type=click.File("r"), default="-")
@click.argument("pattern", type=click.STRING)
@CLIUtil.item_option()
@CLIUtil.ignore_option()
def detail_cmd(
    stdin: IO,
    pattern: str,
    item: tuple[SysCtxItem],
    ignore: tuple[SysCtxItem],
    # config: tuple[RecWeight],
) -> None:
    """詳細."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    tgts = [n for n in sn.g.nodes if pattern in n]
    items = [SysContext.from_item(i) for i in item if i not in ignore]
    # print("#" * 80)
    for tgt in tgts:
        _rets = [it(sn, tgt, 1, 1) for it in items]
        # print(sn.get(tgt))
        # for r in rets:
        #     r.detail()
    # sn = parse2net(txt)


# typerのがいいかどうか... file inputの補完が効かないからclickを使うままにしておく
# def view_vcmd(
#     # stdin: Annotated[typer.FileText, typer.Argument(mode="r")] = sys.stdin,
#     p: Annotated[Path, typer.Argument(mode="r")],
# ) -> None:
#     txt = p.read_text()
#     # sn = try_parse2net(txt)jk
#     sn = parse2net(txt)
#     nxprint(sn.g)
