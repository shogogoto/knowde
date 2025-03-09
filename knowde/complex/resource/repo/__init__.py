"""resource repository."""
from pydantic import RootModel

from knowde.complex.resource import ResourceMeta


class SyncResourceMeta(RootModel[list[ResourceMeta]]):
    """リクエスト用."""


# def sync_namespace(user_id: UUID, meta: SyncResourceMeta) -> NameSpace:
#     """名前空間の同期."""
#     ns = fetch_namespace(user_id)


# def should_update_entries(user_id: UUID, meta: SyncResourceMeta) -> None:
#     """更新すべきリソースを返す."""
