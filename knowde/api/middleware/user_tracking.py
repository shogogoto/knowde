"""Middleware for user tracking."""

import logging
from typing import override

from starlette.middleware.base import BaseHTTPMiddleware

from knowde.api.middleware.logging.context import user_id_var

logger = logging.getLogger(__name__)


class UserTrackingMiddleware(BaseHTTPMiddleware):
    """Track user."""

    @override
    async def dispatch(self, request, call_next):
        """Dispatch the request.

        - Get token from Authorization header or cookie
        - Get user from token
        - Set user_id to context var
        - Reset context var after request
        """
        # token: str | None = None
        # auth_header = request.headers.get("Authorization")
        # if auth_header and auth_header.startswith("Bearer "):
        #     token = auth_header.split(" ")[1]
        # else:
        #     token = request.cookies.get("fastapiusersauth")

        # Reset context var before request
        ctx_token = user_id_var.set(None)
        request.state.user = None

        # if token:
        #     try:
        #         print("@" * 100)
        #         print(request.headers)
        #         print(request.cookies)
        #         user = await auth_component().current_user(active=True)(request)
        #         # user = await auth_component().backends.get_user_from_token(token)
        #         print("#" * 1000)
        #         print(user)
        #         print(user)
        #         print(user)
        #         print(user)
        #         print(user)
        #         if user and user.is_active:
        #             user_id_var.set(user.id)
        #             request.state.user = user
        #             logger.debug(f"User found from token: {user.id}")
        #
        #     except Exception:
        #         logger.debug("Could not validate user from token.")

        response = await call_next(request)

        # Reset context var after request
        user_id_var.reset(ctx_token)
        return response
