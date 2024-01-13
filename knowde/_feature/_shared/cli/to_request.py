from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Optional, ParamSpec, TypeVar

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.param import parametrize

if TYPE_CHECKING:
    from requests import Response

    from knowde._feature._shared.api.param import ApiParam
    from knowde._feature._shared.endpoint import Endpoint

T = TypeVar("T", bound=DomainModel)
P = ParamSpec("P")


def _default_check(_res: Response) -> None:
    pass


class HttpMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

    def request_func(  # noqa: PLR0913
        self,
        ep: Endpoint,
        param: type[ApiParam],
        return_converter: Callable[[Response], Any],
        response_check: Callable[[Response], None] = _default_check,
        post_func: Optional[Callable] = None,
    ) -> Callable:
        def req(**kwargs) -> T | None:  # noqa: ANN003
            method = getattr(ep, self.value)
            res = method(**param.for_method(**kwargs))
            response_check(res)
            if post_func is not None:
                post_func(**kwargs)
            return return_converter(res)

        return parametrize(param, f=req)
