"""単一ファイルの読み込み・表示."""
from __future__ import annotations

from typing import IO, TYPE_CHECKING

import click

from knowde.complex.systats.types import Nw1N1Label

if TYPE_CHECKING:
    from knowde.complex.systats.nw1_n0.scorable import LRWTpl
    from knowde.complex.systats.types import Nw1N1Recursive


@click.group("view")
def view_cli() -> None:
    """ファイル入力に基づく表示."""


@view_cli.command("stat")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option("--heavy", is_flag=True, default=False, help="重い統計値も算出")
@click.option("--table", is_flag=True, default=False, help="テーブル表示")
def stat_cmd(
    stdin: IO,
    heavy: bool,  # noqa: FBT001
    table: bool,  # noqa: FBT001
) -> None:
    """統計値."""
    from .proc import stat_proc

    stat_proc(stdin, heavy, table)


t_choice = click.Choice(tuple(Nw1N1Label))
item_opt = click.option(
    "-i",
    "--item",
    type=t_choice,
    multiple=True,
    default=tuple(Nw1N1Label),
    show_default=True,
    help="表示項目",
)
ignore_opt = click.option(
    "-ig",
    "--ignore",
    type=t_choice,
    multiple=True,
    help="非表示項目",
    show_default=True,
)


@view_cli.command("score")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option(
    "-n",
    "--number",
    type=click.INT,
    default=15,
    help="表示行数数",
    show_default=True,
)
@item_opt
@ignore_opt
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
    from .proc import score_proc

    score_proc(stdin, number, item, ignore, config)


@view_cli.command("detail")
@click.option("--stdin", type=click.File("r"), default="-")
@click.argument("pattern", type=click.STRING)
@item_opt
@ignore_opt
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
    from .proc import detail_proc

    detail_proc(stdin, pattern, item, ignore, config)


@view_cli.command("time")
@click.option("--stdin", type=click.File("r"), default="-")
@click.argument("timespan", type=click.STRING)
@click.option(
    "-o",
    "--overlap",
    is_flag=True,
    default=False,
    help="指定期間と重なるものも表示",
)
def time_cmd(stdin: IO, timespan: str, overlap: bool) -> None:  # noqa: FBT001
    """時系列から指定期間に含まれるものを列挙.

    TIMESPAN EDTF(Extended Date/Time Format)を独自拡張した日付.

    Example:
    -------
    20C => 1901から2000までの範囲.
    "1901 ~ 2000" =>  引数で囲うことでスペースを含めて1つの引数にできる.
    BC100 => 紀元前100の1/1 ~ 12/31.
    -100 => 紀元前、オプションと判定されるからBC表記推奨
    BC2C => 紀元前２世紀(-0199/01/01 ~ 0100/12/31)
    普通のEDTF 参考(https://www.loc.gov/standards/datetime/)
        ex. 19XX => 1900 ~ 1999

    """
    from .proc import time_proc

    if overlap:
        time_proc(stdin, timespan, "overlap")
    else:
        time_proc(stdin, timespan, "envelop")


# # typerのがいいかどうか... file inputの補完が効かないからclickを使うままにしておく
# def view_vcmd(
#     stdin: Annotated[typer.FileText, typer.Argument(mode="r")] = sys.stdin,
#     p: Annotated[Path, typer.Argument(mode="r")],
# ) -> None:
#     txt = p.read_text()
#     # sn = try_parse2net(txt)jk
#     sn = parse2net(txt)
#     nxprint(sn.g)
