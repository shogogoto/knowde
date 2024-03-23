from fastapi import status
from requests import Response

from knowde._feature._shared.api.errors import (
    DeleteFailureError,
    GetFailureError,
    PostFailureError,
    PutFailureError,
)


def _to_message(res: Response) -> str:
    cd = res.status_code
    msg = res.json()["detail"]
    return f"[{cd}]{msg}"


def check_post(res: Response) -> None:
    if res.status_code != status.HTTP_201_CREATED:
        raise PostFailureError(_to_message(res))


def check_get(res: Response) -> None:
    if res.status_code != status.HTTP_200_OK:
        raise GetFailureError(_to_message(res))


def check_put(res: Response) -> None:
    if res.status_code != status.HTTP_200_OK:
        raise PutFailureError(_to_message(res))


def check_delete(res: Response) -> None:
    if res.status_code != status.HTTP_204_NO_CONTENT:
        raise DeleteFailureError(_to_message(res))
