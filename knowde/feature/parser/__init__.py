"""load-file."""

from typing import IO

import click

from knowde.complex.__core__.file_io import nx2json_dump
from knowde.feature.__core__ import try_parse2net

"""
欲しいCLIは?
    フィードバックを得られるもの
        1. 文法チェック
        2. view
            1NW(+別バージョン)のみまず提供するか
            1NW0N
            1NW1N
            1NW2N
            2NW0N
            2NW1N
            2NW2N
        3. 差分

"""


@click.group("input")
def input_group() -> None:
    """テキスト入力."""


@input_group.command("parse")
@click.argument("stdin", type=click.File("r"), default="-")
def parse_cmd(stdin: IO) -> None:
    """入力テキストのパース."""
    txt = stdin.read()
    _sn = try_parse2net(txt)
    js = nx2json_dump(_sn.g)
    print(js)  # noqa: T201
    # g = nxread(js)
    # pr = nx.pagerank(sn.graph)
    # pr = {sn.get(k): v for k, v in pr.items()}
    # pp(pr)
    # pp(sorted(pr.items(), key=lambda i: i[1]))


@input_group.command("view")
@click.argument("stdin", type=click.File("r"), default="-")
# @click.option("-n", "--number", type=click.INT, help="表示数")
def rank_cmd(stdin: IO) -> None:
    """重要度でソート."""
    txt = stdin.read()
    _sn = try_parse2net(txt)
    # chunks = get_ranking(_sn)
    # for c in chunks:
    #     print(c.rank, c)
    # print("#" * 80)
    # for t in [t for t in _sn.terms if not t.has_only_alias]:
    #     print(t)
