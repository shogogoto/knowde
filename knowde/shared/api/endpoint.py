"""API endpoints."""

from __future__ import annotations

import os
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Self
from urllib.parse import urljoin

import requests
from fastapi import APIRouter, status
from inflector import Inflector

if TYPE_CHECKING:
    from knowde.shared.api.types import EndpointMethod

TIMEOUT = 3.0


class Endpoint(Enum):
    """endpoint."""

    Concept = "concept"
    Reference = "reference"
    Book = "reference/book"
    Chapter = "reference/chapter"
    Section = "reference/section"
    RefDef = "reference/definition"
    Sentence = "sentence"
    Definition = "definition"
    Proposition = "proposition"
    Deduction = "deduction"
    Timeline = "timeline"
    Location = "location"
    Person = "person"
    Event = "event"
    Test = "tests"  # test用

    @classmethod
    def of(cls, prefix: str) -> Self:
        """Instantiate from string."""
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
        relative_ = self.value
        if relative is not None and relative:
            relative_ += f"/{relative}"

        try:
            base = os.getenv("KNOWDE_URL", "https://knowde.onrender.com")
            return urljoin(base, relative_)
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
        """To fastapi router."""
        return APIRouter(
            prefix=self.prefix,
            tags=[self.single_form],
        )


def router2tpost(  # noqa: D103
    router: APIRouter,
    f: Callable,
    path: str = "",
) -> EndpointMethod:
    router.post(
        path,
        status_code=status.HTTP_201_CREATED,
    )(f)
    return Endpoint.of(router.prefix).post


def router2put(  # noqa: D103
    router: APIRouter,
    f: Callable,
    path: str = "/{uid}",
) -> EndpointMethod:
    router.put(path)(f)
    return Endpoint.of(router.prefix).put


def router2get(  # noqa: D103
    router: APIRouter,
    f: Callable,
    path: str = "",
) -> EndpointMethod:
    router.get(path)(f)
    return Endpoint.of(router.prefix).get


def router2delete(  # noqa: D103
    router: APIRouter,
    f: Callable,
    path: str = "/{uid}",
) -> EndpointMethod:
    router.delete(
        path,
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
    )(f)
    return Endpoint.of(router.prefix).delete
