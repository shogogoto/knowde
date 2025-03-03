"""永続化前の中間ファイル."""

from pathlib import Path

from pydantic import BaseModel

from knowde.complex.__core__.file_io import nxread, nxwrite
from knowde.complex.__core__.sysnet import SysNet
from knowde.primitive.config import dir_path

"""
networkxのCRUD
"""


class Stage(BaseModel, frozen=True):
    """永続化前中間一時ファイル."""

    def save(self, sn: SysNet) -> None:
        """SysNet -> file."""
        p = dir_path() / sn.root.replace("#", "")
        nxwrite(sn.g, p.with_suffix(".json"))

    def read(self, p: Path) -> SysNet:
        """File -> SysNet."""
        g = nxread(p.read_text())
        return SysNet(root=p.name, g=g)
