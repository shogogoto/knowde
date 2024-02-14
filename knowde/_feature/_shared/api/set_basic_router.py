from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from knowde._feature._shared.api.basic_methods import (
    create_add_and_change,
    create_basic_methods,
)
from knowde._feature._shared.api.types import ReturnType
from knowde._feature._shared.integrated_interface.generate_req import (
    APIRequests,
    inject_signature,
)
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from fastapi import APIRouter
    from pydantic import BaseModel


def set_basic_router(
    util: LabelUtil,
    router: APIRouter,
) -> ReturnType:
    """labelに対応したCRUD APIの基本的な定義."""
    reqs = APIRequests(router=router)

    def add_and_change(t_in: type[BaseModel]) -> None:
        add, ch, Opt = create_add_and_change(util, t_in)  # noqa: N806
        reqs.post(inject_signature(add, [t_in], util.model))
        reqs.put(inject_signature(ch, [UUID, Opt], util.model))

    rm, complete, ls = create_basic_methods(util)
    reqs.delete(inject_signature(rm, [UUID]))
    reqs.get(
        inject_signature(complete, [str], util.model),
        "/completion",
    )
    reqs.get(inject_signature(ls, [], list[util.model]))

    return ReturnType(
        router,
        reqs,
        add_and_change,
    )
