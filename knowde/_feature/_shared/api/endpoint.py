"""API endpoints."""
from __future__ import annotations

import os
from enum import Enum
from typing import Self
from urllib.parse import urljoin

import requests
from fastapi import APIRouter
from inflector import Inflector

TIMEOUT = 3.0


class Endpoint(Enum):
    """endpoint."""

    Concept = "concepts"
    Reference = "references"
    Book = "references/books"
    Chapter = "references/chapters"
    Section = "references/sections"
    RefDef = "references/definitions"
    Sentence = "sentences"
    Definition = "definitions"

    Test = "tests"  # test用

    @classmethod
    def of(cls, prefix: str) -> Self:
        for m in cls:
            if m.prefix == prefix:
                return m
        msg = f"{prefix} must be in {[m.prefix for m in cls]}"
        raise KeyError(msg)

    @property
    def prefix(self) -> str:
        """REST API用."""
        return f"/{self.value}"

    @property
    def single_form(self) -> str:
        """単数形."""
        return Inflector().singularize(self.value)

    def __url(self, relative: str | None = None) -> str:
        _relative = self.value
        if relative is not None and relative != "":
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
        json: object = None,
    ) -> requests.Response:
        """Get of RESTful API."""
        return requests.get(
            self.__url(relative),
            timeout=TIMEOUT,
            params=params,
            json=json,
        )

    def delete(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Delete of Restful API."""
        return requests.delete(
            self.__url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )

    def post(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.post(
            self.__url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )

    def put(
        self,
        relative: str | None = None,
        params: dict | None = None,
        json: object = None,
    ) -> requests.Response:
        """Post of Restful API."""
        return requests.put(
            self.__url(relative),
            timeout=TIMEOUT * 3,
            params=params,
            json=json,
        )

    def create_router(self) -> APIRouter:
        return APIRouter(
            prefix=self.prefix,
            tags=[self.single_form],
        )
