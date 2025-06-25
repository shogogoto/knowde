"""test."""

import json
from functools import cache
from pathlib import Path
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.complex.auth.repo.client import AuthPost
from knowde.primitive.user.repo import LUser


@cache
def read_fixture(filename: str) -> object:  # noqa: D103
    p = Path(__file__).parent / "fixtures" / f"{filename}.json"
    return json.loads(p.read_text())


@pytest.fixture
def client() -> TestClient:  # noqa: D103
    return TestClient(root_router())


TEST_EMAIL = "example@example.org"
TEST_ID = "user_29w83sxmDNGwOuEthce5gg56FcC"


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


def test_crud_user_with_clerk(client: TestClient):
    """先にCLI、後にclerkでユーザー作成してid紐付け."""
    # CREATE
    p = AuthPost(client=client.post)
    # 一部大文字でもちゃんと同じemailとして認識する
    p.register(email="exaMple@example.org", password="password")  # noqa: S106
    client.post("webhook/clerk", json=read_fixture("user_created"))
    users = LUser.nodes.filter(email__iexact=TEST_EMAIL)
    assert len(users) == 1  # 既存のユーザーにidが追加されるのみで重複して作られない
    assert users[0].email == TEST_EMAIL  # 小文字で登録される
    assert users[0].clerk_id == TEST_ID

    # UPDATE
    client.post("webhook/clerk", json=read_fixture("user_updated"))
    users = LUser.nodes.filter(email__iexact=TEST_EMAIL)
    assert len(users) == 1  # 既存のユーザーにidが追加されるのみで重複して作られない
    assert users[0].email == TEST_EMAIL  # 小文字で登録される
    assert users[0].clerk_id == TEST_ID
    assert users[0].display_name == "tanaka taro"

    # DELETE
    client.post("webhook/clerk", json=read_fixture("user_deleted"))
    users = LUser.nodes.filter(email__iexact=TEST_EMAIL)
    assert len(users) == 0


def test_pre_clerk_user(client: TestClient):
    """clerkのユーザーが既存で後からDBユーザー作成."""
    client.post("webhook/clerk", json=read_fixture("user_created"))

    p = AuthPost(client=client.post)
    res = p.register(email="exaMple@example.org", password="password")  # noqa: S106
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    # clerk外で重複してユーザーを作れない
    users = LUser.nodes.filter(email__iexact=TEST_EMAIL)
    assert len(users) == 1
    assert users[0].email == TEST_EMAIL  # 小文字で登録される
    assert users[0].clerk_id == TEST_ID
