"""settings."""
from __future__ import annotations

from typing import Final, Optional
from urllib.parse import urljoin

import requests
from neomodel import config, db, install_all_labels
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEOUT: Final = 3.0


class Settings(BaseSettings):
    """環境変数."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  # 追加
    )

    NEO4J_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SSO_PROT: int = 19419
    KNOWDE_URL: str
    AUTH_SECRET: str = "SECRET"
    JWT_LIFETIME_SEC: int = 60 * 60 * 24  # 1 day

    def setup_db(self) -> None:
        """DB設定."""
        config.DATABASE_URL = self.NEO4J_URL
        install_all_labels()

    def terdown_db(self) -> None:
        """DB切断."""
        if db.driver is not None:
            db.close_connection()

    def url(self, relative: str) -> str:
        """Self server url."""
        return urljoin(self.KNOWDE_URL, relative)

    def get(  # noqa: PLR0913
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """Get of RESTful API."""
        return requests.get(
            self.url(relative),
            timeout=TIMEOUT,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def delete(  # noqa: PLR0913
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """Delete of Restful API."""
        return requests.delete(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def post(  # noqa: PLR0913
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.post(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def put(  # noqa: PLR0913
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.put(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

    def patch(  # noqa: PLR0913
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
        data: object = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        """Patch of RESTful API."""
        return requests.patch(
            self.url(relative),
            timeout=TIMEOUT,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )
