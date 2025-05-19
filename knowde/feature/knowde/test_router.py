"""knowde router test."""

from fastapi import status
from fastapi.testclient import TestClient

from knowde.feature.api import root_router


def test_detail():
    """Knowde detail router test."""
    client = TestClient(root_router())
    res = client.get("/knowde/sentence/064ef00c-5e33-4505-acf5-45ba26cc54dc")
    assert res.status_code == status.HTTP_404_NOT_FOUND
