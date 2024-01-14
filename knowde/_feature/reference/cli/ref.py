from __future__ import annotations

from knowde._feature._shared.api.basic_param import AddParam, ChangeParam
from knowde._feature._shared.cli import create_group
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.domain.domain import Reference

ref_cli, utils = create_group(
    "reference",
    ep=Endpoint.Reference,
    t_model=Reference,
)


class NameParam(AddParam, frozen=True):
    name: str


ref_cli.command("add")(
    utils.create_add(NameParam, "Reference was created newly."),
)


class RenameParam(ChangeParam, frozen=True):
    name: str | None


ref_cli.command("ch")(
    utils.create_change(RenameParam, "Reference was changed 0 -> 1"),
)
