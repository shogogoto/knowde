"""DB."""

from collections.abc import Callable
from uuid import UUID

import httpx
from pydantic import BaseModel

from knowde.config import LocalConfig
from knowde.config.env import Settings
from knowde.feature.user import PREFIX_USER
from knowde.feature.user.errors import TokenUnsavedError

s = Settings()


def auth_header() -> dict:
    """認証リクエスト用ヘッダー."""
    c = LocalConfig.load()
    if not c.CREDENTIALS:
        msg = "認証情報が取得できませんでした"
        raise TokenUnsavedError(msg)
    token = c.CREDENTIALS["access_token"]
    return {"Authorization": f"Bearer {token}"}


class AuthPost(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.post

    def register(  # noqa: D102
        self,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> httpx.Response:
        d = {"email": email, "password": password, "display_name": display_name}
        return self.client("/auth/register", json=d)

    def login(self, email: str, password: str) -> httpx.Response:  # noqa: D102
        d = {"username": email, "password": password}
        return self.client("/auth/jwt/login", data=d)

    def logout(self) -> httpx.Response:  # noqa: D102
        return self.client("/auth/jwt/logout", headers=auth_header())


def save_credential(login_res: httpx.Response) -> None:
    """認証情報のローカルへの保存."""
    if login_res.is_success:
        c = LocalConfig.load()
        c.CREDENTIALS = login_res.json()
        c.save()


class AuthGet(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.get

    def me(self) -> httpx.Response:  # noqa: D102
        return self.client(f"{PREFIX_USER}/me", headers=auth_header())

    def user(self, uid: UUID) -> httpx.Response:  # noqa: D102
        return self.client(f"{PREFIX_USER}/{uid}", headers=auth_header())


class AuthPatch(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.patch

    def change_me(  # noqa: D102
        self,
        email: str | None = None,
        password: str | None = None,
        display_name: str | None = None,
        user_id: str | None = None,
    ) -> httpx.Response:
        d = {
            "email": email,
            "password": password,
            "display_name": display_name,
            "id": user_id,
        }
        d = {k: v for k, v in d.items() if v is not None}
        return self.client(f"{PREFIX_USER}/me", headers=auth_header(), json=d)


# def change_user_proc(
#     uid: UUID,
#     email: str | None,
#     password: str | None,
#     activate: bool | None,
#     tobe_super: bool | None,
#     patch: ReqProtocol = s.patch,
# ) -> Response:
#     """スーパーユーザーによるアカウント情報の変更."""
#     change = {
#         k: v
#         for k, v in {
#             "email": email,
#             "password": password,
#             "is_active": activate,
#             "is_superuser": tobe_super,
#         }.items()
#         if v is not None
#     }

#     token = read_saved_token()
#     return patch(
#         f"/users/{uid}",
#         headers={"Authorization": f"Bearer {token}"},
#         json=change,
#     )
