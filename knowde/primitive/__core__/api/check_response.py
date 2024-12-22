"""responseに対してエラーチェック."""
from fastapi import status
from requests import Response

from knowde.primitive.__core__.api.endpoint import (
    router2delete,
    router2get,
    router2put,
    router2tpost,
)
from knowde.primitive.__core__.api.errors import (
    DeleteFailureError,
    GetFailureError,
    PostFailureError,
    PutFailureError,
)
from knowde.primitive.__core__.api.types import CheckResponse, Router2EndpointMethod


def _to_message(res: Response) -> str:
    cd = res.status_code
    msg = res.json()["detail"]
    return f"[{cd}]{msg}"


def check_post(res: Response) -> None:
    """Post response check for raising error."""
    if res.status_code != status.HTTP_201_CREATED:
        raise PostFailureError(_to_message(res))


def check_get(res: Response) -> None:
    """Get response check for raising error."""
    if res.status_code != status.HTTP_200_OK:
        raise GetFailureError(_to_message(res))


def check_put(res: Response) -> None:
    """Put response check for raising error."""
    if res.status_code != status.HTTP_200_OK:
        raise PutFailureError(_to_message(res))


def check_delete(res: Response) -> None:
    """Delete response check for raising error."""
    if res.status_code != status.HTTP_204_NO_CONTENT:
        raise DeleteFailureError(_to_message(res))


def check_default(r2epm: Router2EndpointMethod) -> CheckResponse:
    """Response checkの基本的なヤツを統合."""
    if r2epm == router2get:
        return check_get
    if r2epm == router2tpost:
        return check_post
    if r2epm == router2put:
        return check_put
    if r2epm == router2delete:
        return check_delete
    msg = "default check response is not found."
    raise ValueError(msg)
