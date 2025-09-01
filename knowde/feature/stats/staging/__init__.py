"""永続化前の中間ファイル."""

from pathlib import Path

from pydantic import BaseModel

from knowde.config.env import Settings
from knowde.feature.parsing.file_io import nxread, nxwrite
from knowde.feature.parsing.sysnet import SysNet

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
        g = nxread(p.read_text(encoding="utf-8"))
        return SysNet(root=p.name, g=g)
