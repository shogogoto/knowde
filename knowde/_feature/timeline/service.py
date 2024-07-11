from __future__ import annotations

from knowde._feature.timeline.domain.domain import TimeValue  # noqa: TCH001
from knowde._feature.timeline.repo.timeline import list_timeline


def list_time_service(
    name: str,
    year: int | None = None,
    month: int | None = None,
) -> list[TimeValue]:
    return list_timeline(name, year, month).values
