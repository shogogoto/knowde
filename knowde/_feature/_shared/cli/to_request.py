from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional, ParamSpec, TypeVar

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

    def request_func(  # noqa: PLR0913
        self,
        ep: Endpoint,
        param: type[ApiParam],
        model: type[T] | None = None,
        response_check: Callable[[Response], None] = default_check,
        post_func: Optional[Callable] = None,
    ) -> Callable:
        def req(**kwargs) -> T | None:  # noqa: ANN003
            method = getattr(ep, self.value)
            res = method(**param.for_method(**kwargs))
            response_check(res)
            if post_func is not None:
                post_func(**kwargs)
            if model is not None:
                return model.model_validate(res.json())
            return None

        return param.makefunc(f=req)
