"""settings."""
from __future__ import annotations

from typing import Final
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
    PORT: int = 8000
    SSO_PROT: int = 19419
    KN_URL: str = "http://localhost"
    AUTH_SECRET: str = "SECRET"

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
        return urljoin(f"{self.KN_URL}:{self.PORT}", relative)

    def get(
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Get of RESTful API."""
        return requests.get(
            self.url(relative),
            timeout=TIMEOUT,
            params=params,
            json=json,
        )

    def delete(
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Delete of Restful API."""
        return requests.delete(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )

    def post(
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.post(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )

    def put(
        self,
        relative: str,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.put(
            self.url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )
