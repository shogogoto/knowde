"""parse tree to sysnet."""
from __future__ import annotations

from knowde.complex.__core__.sysnet import SysNet
from knowde.feature.parser.tree2net.interpreter import SysNetInterpreter
from knowde.feature.parser.tree2net.transformer import TSysArg
from knowde.primitive.parser import parse2tree
from knowde.primitive.parser.testing import treeprint


def parse2net(txt: str, do_print: bool = False) -> SysNet:  # noqa: FBT001 FBT002
    """文からsysnetへ."""
    _t = parse2tree(txt, TSysArg())
    if do_print:
        treeprint(_t, True)  # noqa: FBT003
    si = SysNetInterpreter()
    si.visit(_t)
    return si.sn
