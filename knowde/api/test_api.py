"""test root api."""
from fastapi import status
from fastapi.testclient import TestClient

from .api import api

client = TestClient(api)


def test_catch_error() -> None:
    """Error handling."""
    not_exists = "12345"
    res = client.get(url=f"/concepts/completion?pref_uid={not_exists}")
    assert res.status_code == status.HTTP_404_NOT_FOUND
