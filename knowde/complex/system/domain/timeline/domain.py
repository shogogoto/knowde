"""時系列."""
from pydantic import BaseModel

from knowde.core.types import NXGraph


class TimeSeries(BaseModel):
    """時系列."""

    g: NXGraph
