"""routers."""


from fastapi import APIRouter, Depends

from knowde.complex.auth.routers import auth_component
from knowde.complex.entry.category.folder import NameSpace
from knowde.complex.entry.category.folder.repo import fetch_namespace
from knowde.complex.entry.repo import ResourceMetas, UpdateFileMap, sync_namespace
from knowde.primitive.user import User

entry_router = APIRouter(tags=["entry"])


@entry_router.post("/namespace")
async def sync_paths(
    metas: ResourceMetas,
    user: User = Depends(auth_component().current_user(active=True)),
) -> UpdateFileMap:
    """ファイルシステムと同期."""
    ns = fetch_namespace(user.id)
    return sync_namespace(metas, ns)


@entry_router.get("/namespace")
async def get_namaspace(
    user: User = Depends(auth_component().current_user(active=True)),
) -> NameSpace:
    """ユーザーの名前空間."""
    return fetch_namespace(user.id)
