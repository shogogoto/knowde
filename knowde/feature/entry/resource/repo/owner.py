"""リソース所有者判定."""

from knowde.feature.entry.label import LResource
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.types import UUIDy, to_uuid


async def is_resource_owner(user_uid: UUIDy, resource_uid: UUIDy) -> bool:
    """リソース所有者判定."""
    r = await LResource.nodes.get_or_none(uid=to_uuid(resource_uid).hex)
    if r is None:
        msg = f"リソースが見つかりません: {resource_uid}"
        raise NotFoundError(msg)
    owner = await r.owner.single()
    if owner is None:
        msg = f"リソース{resource_uid}の所有者情報が見つかりません"
        raise NotFoundError(msg)
    return to_uuid(owner.uid) == to_uuid(user_uid)
