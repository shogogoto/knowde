"""googl sso router."""
from functools import cache
from queue import Queue
from typing import Annotated, TypedDict

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.base import SSOBase
from fastapi_sso.sso.google import GoogleSSO
from pydantic_core import Url

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.sso import Provider


class GoogleSSOResponse(TypedDict):
    """SSOレスポンス."""

    id: str
    email: str
    first_name: str
    last_name: str
    display_name: str
    picture: Url
    provider: Provider


def router_google_sso(port: int = 8000) -> APIRouter:
    """GoogleのSingle sign on用."""
    router_sso = APIRouter(tags=["Google SSO"])
    callurl = "/google/callback"
    s = Settings()

    def google_sso() -> GoogleSSO:
        """For depends."""
        return GoogleSSO(
            s.GOOGLE_CLIENT_ID,
            s.GOOGLE_CLIENT_SECRET,
            f"http://localhost:{port}{callurl}",
        )

    @router_sso.get("/google/login")
    async def google_login(
        sso: Annotated[SSOBase, Depends(google_sso)],
    ) -> RedirectResponse:
        """Google login."""
        async with sso:
            return await sso.get_login_redirect()

    @router_sso.get(callurl)
    async def google_callback(
        request: Request,
        sso: Annotated[SSOBase, Depends(google_sso)],
    ) -> Response:
        """Google callback."""
        async with sso:
            user = await sso.verify_and_process(request)
            if user is None:
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=_content("認証失敗orz"),
                    media_type="text/html",
                )
            response_queue().put(user)
            return Response(
                content=_content("認証成功！"),  # noqa: RUF001
                media_type="text/html",
            )

    return router_sso


@cache
def response_queue() -> Queue:
    """レスポンスを保存するためのグローバルキュー."""
    return Queue()


def _content(msg: str) -> str:
    return f"""
        <html>
            <body>
                <h2>{msg}</h2>
            </body>
        </html>
    """
