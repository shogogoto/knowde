"""API endpoints."""
from __future__ import annotations

import os
from enum import Enum
from urllib.parse import urljoin

import requests

TIMEOUT = 3.0


class Endpoint(Enum):
    """endpoint."""

    Concept = "concepts"

    def __url(self, relative: str | None = None) -> str:
        _relative = self.value
        if relative is not None:
            _relative += f"/{relative}"

        try:
            base = os.getenv("KNOWDE_URL", "https://knowde.onrender.com")
            return urljoin(base, _relative)
        except KeyError as e:
            msg = "KNOWDE_URL環境変数にAPIのURLを設定してください"
            raise KeyError(msg) from e

    def get(
        self,
        relative: str | None = None,
        params: dict | None = None,
    ) -> requests.Response:
        """Get of RESTful API."""
        return requests.get(
            self.__url(relative),
            timeout=TIMEOUT,
            params=params,
        )

    def delete(self, relative: str) -> requests.Response:
        """Delete of Restful API."""
        return requests.delete(
            self.__url(relative),
            timeout=TIMEOUT * 3,
        )

    def post(
        self,
        relative: str | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.post(
            self.__url(relative),
            timeout=TIMEOUT * 3,
            json=json,
        )

    def put(
        self,
        relative: str | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.put(
            self.__url(relative),
            timeout=TIMEOUT * 3,
            json=json,
        )
