from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from knowde._feature._shared.cli.click_wrapper import to_click_wrappers
from knowde._feature._shared.domain import DomainModel

if TYPE_CHECKING:
    from httpx import Response

    from knowde._feature._shared.api.param import ApiParam
    from knowde._feature._shared.endpoint import Endpoint

T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


def default_check(_res: Response) -> None:
    pass


class HttpMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

    def request_func(
        self,
        ep: Endpoint,
        model: type[T],
        param: type[ApiParam],
        response_check: Callable[[Response], None] = default_check,
    ) -> Callable:
        def req(**kwargs) -> T:  # noqa: ANN003
            method = getattr(ep, self.value)
            res = method(**kwargs)
            response_check(res)
            return model.model_validate(res.json)

        f = param.makefunc(f=req)
        return to_click_wrappers(param).wraps(f)
