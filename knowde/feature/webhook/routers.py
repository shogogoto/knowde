"""API router."""

from fastapi import APIRouter, HTTPException, status

from knowde.complex.auth.routers import auth_component
from knowde.feature.webhook import ClerkEventType, ClerkPayload
from knowde.primitive.user import User
from knowde.primitive.user.repo import LUser

router = APIRouter(prefix="/webhook", tags=["webhook"])


def webhook_router() -> APIRouter:
    """LSP補完用に関数化."""
    return router


@router.post("/clerk")
async def clerk_webhook(payload: ClerkPayload) -> User | None:
    """ClerkでのUser CRUDがwebhookでこのAPIに連携される."""
    manager = auth_component().get_user_manager()
    user = LUser.nodes.get_or_none(clerk_id=payload.user_id)
    if payload.type == ClerkEventType.USER_DELTETED:
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        u = User.from_lb(user)
        await manager.delete(u, None)
    user = user or LUser.nodes.get_or_none(
        email=payload.email,
    )
    if user is None:
        user = LUser(email=payload.email, clerk_id=payload.user_id)
    else:  # 既にユーザーあり
        user.clerk_id = payload.user_id
    return User.from_lb(user.save())

    # await adb.create({
    #     "email": email,
    #     "clerk_id": clerk_user_id,
    # })
