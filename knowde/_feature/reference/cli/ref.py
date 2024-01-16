from __future__ import annotations

from knowde._feature._shared.api.basic_param import AddParam
from knowde._feature._shared.cli import create_group
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.reference.domain.domain import Reference

ref_cli, hooks = create_group(
    "reference",
    ep=Endpoint.Reference,
    t_model=Reference,
)


class NameParam(AddParam, frozen=True):
    name: str


hooks.create_add("add", NameParam, "Reference was created newly.")
hooks.create_change("ch", NameParam, None)
