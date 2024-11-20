"""時系列."""

from typing import Final

from pydantic import BaseModel

from knowde.core.types import NXGraph

# = Anno Domini, 主の年に, 西暦紀元後
SOCIETY_TIMELINE: Final = "AD"


class TimeSeries(BaseModel):
    """時系列."""

    g: NXGraph
