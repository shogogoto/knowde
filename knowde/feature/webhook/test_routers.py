"""test."""

import json
from pathlib import Path
from uuid import UUID

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from knowde.feature.webhook.routers import webhook_router
from knowde.primitive.user.repo import LUser


def read_fixture(filename: str) -> object:  # noqa: D103
    p = Path(__file__).parent / "fixtures" / f"{filename}.json"
    return json.loads(p.read_text())


# @pytest.fixtur
@pytest.fixture
def client() -> TestClient:  # noqa: D103
    api = FastAPI()
    api.include_router(webhook_router())
    return TestClient(api)


def test_clerk_email_created(client: TestClient):  # noqa: D103
    res = client.post("webhook/clerk", json=read_fixture("email_created"))
    assert LUser.nodes.get(uid=UUID(res.json()["uid"]).hex)


def test_clerk_user_created(client: TestClient):  # noqa: D103
    res = client.post("webhook/clerk", json=read_fixture("user_created"))
    assert LUser.nodes.get(uid=UUID(res.json()["uid"]).hex)


def test_clerk_user_updated(client: TestClient):  # noqa: D103
    res = client.post("webhook/clerk", json=read_fixture("user_updated"))
    assert LUser.nodes.get(uid=UUID(res.json()["uid"]).hex)


def test_clerk_user_deleted(client: TestClient):  # noqa: D103
    res = client.post("webhook/clerk", json=read_fixture("user_deleted"))
    assert res.status_code == status.HTTP_404_NOT_FOUND
