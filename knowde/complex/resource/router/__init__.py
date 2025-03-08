"""routers."""


from fastapi import APIRouter, Depends
from pydantic import RootModel

from knowde.complex.auth.routers import auth_component
from knowde.complex.resource.category.folder.repo import fetch_namespace
from knowde.complex.resource.nx2db.save import ResourceMeta
from knowde.primitive.user import User

entry_router = APIRouter(tags=["entry"])


class SyncFilesData(RootModel[list[ResourceMeta]]):
    """リクエスト用."""


@entry_router.post("/namespace")
async def sync_fs(
    sync_data: SyncFilesData,
    user: User = Depends(auth_component().current_user(active=True)),
) -> dict:
    """ファイルシステムと同期."""
    ns = fetch_namespace(user.id)
    for d in sync_data.root:
        if d.path is None:
            continue
        got = ns.get_or_none(*d.path)
        if got is None:  # 新規作成
            pass
    return {}
