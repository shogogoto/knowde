"""repo."""

from knowde.feature.entry.resource.repo.diff_update.domain import (
    UpdateDiff,
    create_edgediff,
)
from knowde.feature.parsing.sysnet import SysNet


async def update_resource_diff(old: SysNet, new: SysNet):  # noqa: RUF029
    """更新差分の反映."""
    termdiff = UpdateDiff.terms(old, new)
    sentdiff = UpdateDiff.sentences(old, new)
    edgediff = create_edgediff(old, new)

    # print("#" * 100)
    # print(termdiff)
    # print(sentdiff)
    # print(edgediff)

    return termdiff, sentdiff, edgediff
