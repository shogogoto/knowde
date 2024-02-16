from __future__ import annotations

import click


@click.group("reference")
def ref_cli() -> None:
    pass


# ref_cli, hooks = create_group(
#     "reference",
#     ep=Endpoint.Reference,
#     t_out=Reference,
# )


# class NameParam(BaseModel, frozen=True):
#     name: str


# hooks.create_add("add", NameParam, "Reference was created newly.")
# hooks.create_change("ch", NameParam, None)
