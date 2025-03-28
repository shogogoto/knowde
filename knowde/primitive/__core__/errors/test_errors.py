"""test."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde.primitive.__core__.errors.errors import DomainError, ErrorHandlingMiddleware

app = FastAPI()
app.add_middleware(ErrorHandlingMiddleware)


MSG = "user defined message"
CD = 400


class UserDefError(DomainError):  # noqa: D101
    status_code = CD
    msg = MSG


@app.get("/test")
def for_test() -> None:  # noqa: D103
    raise UserDefError


@app.get("/test2")
def for_test2() -> None:  # noqa: D103
    msg = "from arg"
    raise UserDefError(msg)


client = TestClient(app)


def test_api() -> None:  # noqa: D103
    res = client.get(url="/test")
    assert res.status_code == CD
    assert res.json()["detail"]["code"] == CD
    assert res.json()["detail"]["message"] == MSG


def test_api2() -> None:  # noqa: D103
    res = client.get(url="/test2")
    assert res.status_code == CD
    assert res.json()["detail"]["code"] == CD
    assert res.json()["detail"]["message"] == "from arg"
