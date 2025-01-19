"""load-file."""
from __future__ import annotations

import json
from typing import IO

import click

from knowde.complex.systats.nw1_n0 import Systats, UnificationRatio
from knowde.complex.systats.nw1_n0.scorable import (
    LRWTpl,
    Nw1N1Label,
    SyScore,
)
from knowde.complex.systats.nw1_n1.ctxdetail import (
    Nw1N1Detail,
    Nw1N1Recursive,
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
    type=(Nw1N1Label, click.INT, click.INT),
    multiple=True,
    help="(項目,再帰回数,重み)",
)
def score_cmd(
    stdin: IO,
    number: int,
    item: tuple[Nw1N1Label],
    ignore: tuple[Nw1N1Label],
    config: tuple[LRWTpl],
) -> None:
    """ノードの文脈スコア順に表示."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    ctx = SyScore.create(item, ignore, config)
    echo_table(ctx.to_json(sn, num=number))


@click.command("detail")
@click.option("--stdin", type=click.File("r"), default="-")
@click.argument("pattern", type=click.STRING)
@CLIUtil.item_option()
@CLIUtil.ignore_option()
@click.option(
    "-c",
    "--config",
    type=(Nw1N1Label, click.INT),
    multiple=True,
    help="(項目,再帰回数)",
)
def detail_cmd(
    stdin: IO,
    pattern: str,
    item: tuple[Nw1N1Label],
    ignore: tuple[Nw1N1Label],
    config: tuple[Nw1N1Recursive],
) -> None:
    """文字列にマッチするノードの詳細."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    detail = Nw1N1Detail.create(item, ignore, config)
    match = sn.match(pattern)
    for i, tgt in enumerate(match):
        click.echo(f"{i+1}. " + detail.format(sn, tgt))
    click.echo(f"{len(match)}件ヒットしました")

    # click.echo(
    #     json.dumps(
    #         apply_nest([detail.ctx_dict(sn, m) for m in match], str),
    #         indent=2,
    #         ensure_ascii=False,
    #     ),
    # )


# # typerのがいいかどうか... file inputの補完が効かないからclickを使うままにしておく
# def view_vcmd(
#     stdin: Annotated[typer.FileText, typer.Argument(mode="r")] = sys.stdin,
#     p: Annotated[Path, typer.Argument(mode="r")],
# ) -> None:
#     txt = p.read_text()
#     # sn = try_parse2net(txt)jk
#     sn = parse2net(txt)
#     nxprint(sn.g)
