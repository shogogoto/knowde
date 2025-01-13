"""load-file."""

from contextlib import contextmanager
from cProfile import Profile
from pprint import pp
from typing import IO

import click

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.systats import Systats, UnificationRatio

"""
NW1
    N0 ここ実装
        重み付け
        recursive n回
"""


@contextmanager
def _profile():  # noqa: ANN202
    pr = Profile()
    pr.enable()
    try:
        yield pr
    finally:
        pr.disable()
        pr.print_stats(sort="tottime")


@click.command("view")
@click.argument("stdin", type=click.File("r"), default="-")
@click.option("-n", "--number", type=click.INT, default=50, help="表示数")
def view_cmd(stdin: IO, number: int) -> None:
    """重要度でソート."""
    with _profile():
        txt = stdin.read()
        # sn = try_parse2net(txt)
        sn = parse2net(txt)
        # nxprint(sn.g)
        number  # noqa: B018
        pp({r.label: r.fn(sn) for r in UnificationRatio})
        pp({r.label: r.fn(sn) for r in Systats})
    # pp({st.label: st.fn(sn) for st in Systats})


# @click.command("parse")
# @click.argument("stdin", type=click.File("r"), default="-")
# def parse_cmd(stdin: IO) -> None:
#     """入力テキストのパース."""
#     txt = stdin.read()
#     _sn = try_parse2net(txt)
#     js = nx2json_dump(_sn.g)
#     print(js)
