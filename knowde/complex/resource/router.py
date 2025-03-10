"""routers."""


from fastapi import APIRouter, Depends

from knowde.complex.auth.routers import auth_component
from knowde.complex.resource.category.folder import NameSpace
from knowde.complex.resource.category.folder.repo import fetch_namespace
from knowde.complex.resource.repo import ResourceMetas
from knowde.primitive.user import User

entry_router = APIRouter(tags=["entry"])


@entry_router.post("/namespace")
async def sync_paths(
    sync_data: ResourceMetas,
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


@entry_router.get("/namespace")
async def get_namaspace(
    user: User = Depends(auth_component().current_user(active=True)),
) -> NameSpace:
    """ユーザーの名前空間."""
    return fetch_namespace(user.id)
