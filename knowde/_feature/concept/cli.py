"""concept cli."""
from __future__ import annotations

import click

from knowde._feature._shared.api.basic_param import CompleteParam
from knowde._feature._shared.cli import set_basic_commands
from knowde._feature._shared.cli.click_wrapper import to_click_wrappers
from knowde._feature._shared.cli.to_request import HttpMethod
from knowde._feature._shared.cli.view.options import view_options
from knowde._feature._shared.endpoint import Endpoint
from knowde._feature.concept.domain import Concept, ConceptProp
from knowde._feature.concept.domain.domain import ChangeProp, ConceptChangeParam


@click.group("concept")
def concept_cli() -> None:
    pass


_, utils = set_basic_commands(
    concept_cli,
    ep=Endpoint.Concept,
    t_model=Concept,
)


# createではなくaddの方がは打数が少ない
concept_cli.command("add")(
    utils.create_add(ConceptProp, "Concept was created newly."),
)


# concept_cli.command("ch")(
#     utils.create_change(ChangeProp, "Concept was changed 0 -> 1"),
# )


@concept_cli.command("ch")
@to_click_wrappers(CompleteParam).wraps
@to_click_wrappers(ChangeProp).wraps
@view_options
def change(
    pref_uid: str,
    name: str | None,
    explain: str | None,
) -> list[Concept]:
    """Change concept properties."""
    pre = utils.complete(pref_uid)
    put = HttpMethod.PUT.request_func(
        ep=Endpoint.Concept,
        param=ConceptChangeParam,
        return_converter=lambda res: Concept.model_validate(res.json()),
    )
    post = put(
        uid=pre.valid_uid,
        name=name,
        explain=explain,
    )
    click.echo("Concept was changed 0 -> 1")
    return [pre, post]
