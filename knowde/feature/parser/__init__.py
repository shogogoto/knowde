"""load-file."""

from pprint import pp
from typing import IO

import click

from knowde.complex.__core__.file_io import nx2json_dump
from knowde.complex.systats import Systats, UnificationRatio
from knowde.feature.__core__ import try_parse2net


@click.command("parse")
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


@click.command("view")
@click.argument("stdin", type=click.File("r"), default="-")
# @click.option("-n", "--number", type=click.INT, help="表示数")
def rank_cmd(stdin: IO) -> None:
    """重要度でソート."""
    txt = stdin.read()
    sn = try_parse2net(txt)
    pp({r.label: r.fn(sn) for r in UnificationRatio})
    pp({st.label: st.fn(sn) for st in Systats})
    # chunks = get_ranking(_sn)
    # for c in chunks:
    #     print(c.rank, c)
    # print("#" * 80)
    # for t in [t for t in _sn.terms if not t.has_only_alias]:
    #     print(t)
