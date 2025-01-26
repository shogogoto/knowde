"""CLIの補完がimportがあると遅くなるので、処理部分を独立させる."""
from __future__ import annotations

import json
from typing import IO, TYPE_CHECKING

import click

from knowde.complex.systats.nw1_n0 import Nw1N0Label
from knowde.complex.systats.nw1_n0.scorable import LRWTpl, SyScore
from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Detail, Nw1N1Recursive
from knowde.feature.__core__ import try_parse2net
from knowde.feature.__core__.cliutil import echo_table

if TYPE_CHECKING:
    from knowde.complex.systats.nw1_n1.ctxdetail import Nw1N1Label


def stat_proc(
    stdin: IO,
    heavy: bool,  # noqa: FBT001
    table: bool,  # noqa: FBT001
) -> None:
    """統計値."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    labels = Nw1N0Label.standard()
    if heavy:
        labels += Nw1N0Label.heavy()

    stat = Nw1N0Label.to_dict(sn, labels)
    if table:
        echo_table([stat])
    else:
        click.echo(json.dumps(stat, indent=2))


def score_proc(  # noqa: D103
    stdin: IO,
    number: int,
    item: tuple[Nw1N1Label],
    ignore: tuple[Nw1N1Label],
    config: tuple[LRWTpl],
) -> None:
    txt = stdin.read()
    sn = try_parse2net(txt)
    ctx = SyScore.create(item, ignore, config)
    echo_table(ctx.to_json(sn, num=number))


def detail_proc(
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
