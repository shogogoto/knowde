from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable

from fastapi import status

if TYPE_CHECKING:
    from uuid import UUID

    from pydantic import BaseModel

    from knowde._feature._shared.api.types import (
        CheckResponse,
        Complete,
        ListClient,
        Remove,
        RequestMethod,
    )
    from knowde._feature._shared.domain import DomainModel


def complete_client(
    req: RequestMethod,
    t_out: type[DomainModel],
) -> Complete:
    def complete(pref_uid: str) -> t_out:
        res = req(
            relative="/completion",
            params={"pref_uid": pref_uid},
        )
        if res.status_code != status.HTTP_200_OK:
            msg = res.json()["detail"]["message"]
            msg = f"[{res.status_code}]:{msg}"
            print(msg)  # noqa: T201
            sys.exit()
        return t_out.model_validate(res.json())

    return complete


def list_client(
    req: RequestMethod,
    t_out: type[DomainModel],
    t_in: type[BaseModel] | None = None,
    check_response: CheckResponse | None = None,
) -> ListClient:
    def ls(**kwargs) -> list[t_out]:  # noqa: ANN003
        if t_in is None:
            res = req()
        else:
            p = t_in.model_validate(kwargs)
            res = req(json=p.model_dump())
        if check_response is not None:
            check_response(res)
        return [t_out.model_validate(e) for e in res.json()]

    return ls


def remove_client(
    req: RequestMethod,
) -> Remove:
    def rm(uid: UUID) -> None:
        req(relative=uid.hex)

    return rm


def add_client(
    req: RequestMethod,
    t_in: type[BaseModel],
    t_out: type[DomainModel],
    check_response: CheckResponse | None = None,
) -> Callable:
    def add(**kwargs) -> t_out:  # noqa: ANN003
        p = t_in.model_validate(kwargs)
        res = req(json=p.model_dump())
        if check_response is not None:
            check_response(res)
        return t_out.model_validate(res.json())

    return add


def change_client(
    req: RequestMethod,
    t_in: type[BaseModel],
    t_out: type[DomainModel],
    complete: Complete,
) -> Callable:
    def change(pref_uid: str, **kwargs) -> tuple[t_out, t_out]:  # noqa: ANN003
        pre = complete(pref_uid)
        res = req(
            relative=pre.valid_uid.hex,
            json=t_in.model_validate(kwargs).model_dump(),
        )
        post = t_out.model_validate(res.json())
        return pre, post

    return change
