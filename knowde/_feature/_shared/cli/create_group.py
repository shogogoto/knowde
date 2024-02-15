from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    TypeVar,
)

import click

from knowde._feature._shared.domain import DomainModel

from . import each_args

if TYPE_CHECKING:
    from knowde._feature._shared.api.types import (
        Complete,
        Remove,
    )


T = TypeVar("T", bound=DomainModel)


def to_command(
    name: str,
    f: Callable,
    helpmsg: str | None = None,
) -> click.Command:
    """ただのショートカット."""
    return click.command(name, help=helpmsg)(f)


def rm_clifunc(
    rm: Remove,
    complete: Complete,
) -> Callable:
    return each_args(
        "uids",
        converter=lambda pref_uid: complete(pref_uid).valid_uid,
    )(rm)


# def create_basic_commands(
#     g: click.Group,
#     clients: BasicClients,
# ) -> None:
#     rm_cli = each_args(
#         "uids",
#         converter=lambda pref_uid: complete(pref_uid).valid_uid,
#     )(clients.rm)

#     def create_add(
#         t_in: type[BaseModel],
#     ) -> Callable:
#         @model2decorator(t_in)
#         @view_options
#         def _add(**kwargs) -> t_out:
#             p = t_in.validate(kwargs)
#             res = ep.post(json=p.model_dump())
#             m = t_out.model_validate(res.json())
#             click.echo(f"{t_out.__name__} was created newly.")
#             return m

#         return _add
#         # c_help: str | None = f"Change {t_model.__name__} properties",

#     def create_change(
#         t_in: type[BaseModel],
#     ) -> Callable:
#         @model2decorator(CompleteParam)
#         @model2decorator(create_partial_model(t_in))
#         @view_options
#         def _change(
#             pref_uid: str,
#             **kwargs,
#         ) -> list[t_out]:
#             pre = complete(pref_uid)
#             d = t_in.model_validate(kwargs).model_dump()
#             res = ep.put(
#                 relative=pre.valid_uid.hex,
#                 json=d,
#             )
#             post = t_out.model_validate(res.json())
#             click.echo(f"{t_out.__name__} was changed from 0 to 1.")
#             return [pre, post]

#         return _change
