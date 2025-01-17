"""load-file."""
from __future__ import annotations

import json
from typing import IO

import click

from knowde.complex.systats.nw1_n0 import Systats, UnificationRatio
from knowde.complex.systats.nw1_n0.syscontext import (
    Nw1N1Label,
    RecursiveWeight,
    SysContexts,
)
from knowde.feature.__core__ import try_parse2net
from knowde.feature.__core__.cliutil import CLIUtil, echo_table


@click.command("stat")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option("--table", is_flag=True, default=False, help="テーブル表示")
def stat_cmd(
    stdin: IO,
    table: bool,  # noqa: FBT001
) -> None:
    """統計値."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    stat = Systats.to_dict(sn) | UnificationRatio.to_dictstr(sn)
    if table:
        echo_table([stat])
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
    # type=click.Tuple([SysCtxItem, click.INT, click.INT]),
    type=(Nw1N1Label, click.INT, click.INT),
    multiple=True,
    help="(項目,再帰回数,重み)",
)
def score_cmd(
    stdin: IO,
    number: int,
    item: tuple[Nw1N1Label],
    ignore: tuple[Nw1N1Label],
    config: tuple[RecursiveWeight],
) -> None:
    """スコアでソート."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    ctx = SysContexts.create(item, ignore, config)
    echo_table(ctx.to_json(sn, num=number))


@click.command("detail")
@click.option("--stdin", type=click.File("r"), default="-")
@click.argument("pattern", type=click.STRING)
@CLIUtil.item_option()
@CLIUtil.ignore_option()
def detail_cmd(
    stdin: IO,
    pattern: str,
    item: tuple[Nw1N1Label],
    ignore: tuple[Nw1N1Label],
    # config: tuple[RecWeight],
) -> None:
    """詳細."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    _ctx = SysContexts.create(item, ignore)

    for _tgt in sn.match(pattern):
        pass
        # _rets = [it(sn, tgt, 1, 1) for it in item]
        # a = sn.get(tgt)
        # print(tgt)
        # print(a)
        # if pattern in str(a):
        #     print(a)
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
