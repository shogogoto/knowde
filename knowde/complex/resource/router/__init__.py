"""routers."""


from fastapi import APIRouter, Depends

from knowde.complex.auth.routers import auth_component
from knowde.primitive.user import User

entry_router = APIRouter(tags=["entry"])


@entry_router.post("/sync")
async def sync_fs(
    _user: User = Depends(auth_component().current_user(active=True)),
) -> None:
    """ファイルシステムと同期."""
