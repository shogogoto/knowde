"""永続化前の中間ファイル."""

from pathlib import Path

from pydantic import BaseModel

from knowde.feature.parsing.file_io import nxread, nxwrite
from knowde.feature.parsing.sysnet import SysNet
from knowde.primitive.config.env import Settings

s = Settings()


class Stage(BaseModel, frozen=True):
    """永続化前中間一時ファイル."""

    @staticmethod
    def save(sn: SysNet) -> None:
        """SysNet -> file."""
        p = s.config_dir / sn.root.replace("#", "")
        nxwrite(sn.g, p.with_suffix(".json"))

    @staticmethod
    def read(p: Path) -> SysNet:
        """File -> SysNet."""
        g = nxread(p.read_text())
        return SysNet(root=p.name, g=g)
