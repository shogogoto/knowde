"""DB."""


from typing import Callable, TypedDict
from uuid import UUID

import httpx
from pydantic import BaseModel

from knowde.complex.auth.errors import TokenUnsavedError
from knowde.primitive.config import LocalConfig
from knowde.primitive.config.env import Settings

s = Settings()


class AuthArgs(TypedDict):
    """ログイン情報."""

    email: str
    password: str


class OptionalInfo(AuthArgs, total=False):  # noqa: D101
    pass


def auth_header() -> dict:
    """認証リクエスト用ヘッダー."""
    c = LocalConfig.load()
    if not c.CREDENTIALS:
        raise TokenUnsavedError
    token = c.CREDENTIALS["access_token"]
    return {"Authorization": f"Bearer {token}"}


class AuthPost(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.post

    def register(self, info: AuthArgs) -> httpx.Response:  # noqa: D102
        return self.client("/auth/register", json=info)

    def login(self, info: AuthArgs) -> httpx.Response:  # noqa: D102
        d = {"username": info["email"], "password": info["password"]}
        return self.client("/auth/jwt/login", data=d)

    def logout(self) -> httpx.Response:  # noqa: D102
        return self.client("/auth/jwt/logout", headers=auth_header())


def save_credentials(login_res: httpx.Response) -> None:
    """認証情報のローカルへの保存."""
    if login_res.is_success:
        c = LocalConfig.load()
        c.CREDENTIALS = login_res.json()
        c.save()
        return
    raise


class AuthGet(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.get

    def me(self) -> httpx.Response:  # noqa: D102
        return self.client("/users/me", headers=auth_header())

    def user(self, uid: UUID) -> httpx.Response:  # noqa: D102
        return self.client(f"/users/{uid}", headers=auth_header())


class AuthPatch(BaseModel):
    """認証client."""

    client: Callable[..., httpx.Response] = s.patch

    def change_me(self, info: OptionalInfo) -> httpx.Response:  # noqa: D102
        d = {k: v for k, v in info.items() if v is not None}
        return self.client("/users/me", headers=auth_header(), json=d)


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
