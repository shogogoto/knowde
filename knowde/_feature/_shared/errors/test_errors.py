from fastapi import FastAPI
from fastapi.testclient import TestClient

from knowde._feature._shared.errors.errors import DomainError, ErrorHandlingMiddleware

app = FastAPI()
app.add_middleware(ErrorHandlingMiddleware)


MSG = "user defined message"
CD = 400


class UserDefError(DomainError):
    status_code = CD
    msg = MSG


@app.get("/test")
def for_test() -> None:
    raise UserDefError


@app.get("/test2")
def for_test2() -> None:
    msg = "from arg"
    raise UserDefError(msg)


client = TestClient(app)


def test_api() -> None:
    res = client.get(url="/test")
    assert res.status_code == CD
    assert res.json()["detail"]["code"] == CD
    assert res.json()["detail"]["message"] == MSG


def test_api2() -> None:
    res = client.get(url="/test2")
    assert res.status_code == CD
    assert res.json()["detail"]["code"] == CD
    assert res.json()["detail"]["message"] == "from arg"
