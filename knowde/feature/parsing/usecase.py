"""CLIの補完がimportがあると遅くなるので、処理部分を独立させる."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING

import click
from tabulate import tabulate

from knowde.feature.parsing.domain import try_parse2net
from knowde.feature.stats.systats.nw1_n1.ctxdetail import Nw1N1Detail
from knowde.feature.stats.systats.nw1_n1.scorable import NRecursiveWeight, SyScore
from knowde.shared.nxutil.edge_type import EdgeType

if TYPE_CHECKING:
    from knowde.feature.stats.systats.types import Nw1N1Label, Nw1N1Recursive


def echo_table(ls: list[dict]) -> None:
    """Echo by tabulate."""
    click.echo(tabulate(ls, headers="keys"))


def score_proc(  # noqa: D103
    stdin: IO,
    number: int,
    item: tuple[EdgeType],
    ignore: tuple[EdgeType],
    config: tuple[NRecursiveWeight],
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
        click.echo(f"{i + 1}. " + detail.format(sn, tgt))
    click.echo(f"{len(match)}件ヒットしました")

    # click.echo(
    #     json.dumps(
    #         apply_nest([detail.ctx_dict(sn, m) for m in match], str),
    #         indent=2,
    #         ensure_ascii=False,
    #     ),
    # )


def time_proc(stdin: IO, timespan: str, method_name: str) -> None:
    """時系列表示."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    ls = [
        {
            "time": str(d),
            "sentence": sn.get(EdgeType.WHEN.get_pred_or_none(sn.g, d)),
        }
        for d in getattr(sn.series, method_name)(timespan)
    ]

    click.echo(tabulate(ls, headers="keys", showindex=True))
