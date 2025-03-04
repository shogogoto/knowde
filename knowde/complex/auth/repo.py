"""DB."""


from typing import TypedDict

import httpx
from pydantic import BaseModel

from knowde.complex.auth.errors import TokenUnsavedError
from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import ReqProtocol, Settings

s = Settings()


class LogInfo(TypedDict):
    """ログイン情報."""

    email: str
    password: str


def auth_header() -> dict:
    """認証リクエスト用ヘッダー."""
    c = LocalConfig.load()
    if not c.CREDENTIALS:
        raise TokenUnsavedError
    token = c.CREDENTIALS["access_token"]
    return {"Authorization": f"Bearer {token}"}


class AuthClient(BaseModel):
    """ユーザー関連."""

    post: ReqProtocol = s.post

    def register(self, **info: LogInfo) -> httpx.Response:  # noqa: D102
        return self.post("/auth/register", json=info)

    def login(self, **info: LogInfo) -> httpx.Response:  # noqa: D102
        return self.post("/auth/jwt/login", data=info)

    def logout(self) -> httpx.Response:  # noqa: D102
        return self.post("/auth/jwt/logout", headers=auth_header())

    def me(self) -> httpx.Response:  # noqa: D102
        pass

    # def me(self) -> httpx.Response:
    #     pass

    # def me(self) -> httpx.Response:
    #     pass
