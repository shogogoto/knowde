"""settings."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, Protocol
from urllib.parse import urljoin

import httpx
from neomodel import config, db
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEOUT: Final = 3.0


class Settings(BaseSettings):
    """環境変数."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  # 追加
        # env_prefix=
    )

    NEO4J_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    KNOWDE_URL: str = "https://knowde.onrender.com/"
    KN_AUTH_SECRET: str = "SECRET"  # noqa: S105
    KN_TOKEN_LIFETIME_SEC: int = 60 * 60 * 24  # 1 day
    CLERK_SECRET_KEY: str

    def setup_db(self) -> None:
        """DB設定."""
        config.DATABASE_URL = self.NEO4J_URL

    @staticmethod
    def terdown_db() -> None:
        """DB切断."""
        if db.driver is not None:
            db.close_connection()

    def url(self, relative: str) -> str:
        """Self server url."""
        return urljoin(self.KNOWDE_URL, relative)

    def get(
        self,
        relative: str,
        params: dict | None = None,
        headers: dict | None = None,
        client: Callable[..., httpx.Response] = httpx.get,
    ) -> httpx.Response:
        """Get of RESTful API."""
        return client(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            headers=headers,
        )

    def delete(  # noqa: PLR0917
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: dict | None = None,
        client: Callable[..., httpx.Response] = httpx.delete,
    ) -> httpx.Response:
        """Delete of Restful API."""
        return client(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def post(  # noqa: PLR0917
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: dict | None = None,
        client: Callable[..., httpx.Response] = httpx.post,
    ) -> httpx.Response:
        """Post of Restful API."""
        return client(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def put(  # noqa: PLR0917
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: dict | None = None,
        client: Callable[..., httpx.Response] = httpx.put,
    ) -> httpx.Response:
        """Post of Restful API."""
        return client(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def patch(  # noqa: PLR0917
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: dict | None = None,
        client: Callable[..., httpx.Response] = httpx.patch,
    ) -> httpx.Response:
        """Patch of RESTful API."""
        return client(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )


class ReqProtocol(Protocol):
    """APIメソッド."""

    def __call__(
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: dict | None = None,
    ) -> httpx.Response:
        """Request."""
        ...
