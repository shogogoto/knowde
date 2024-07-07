"""deduction interface."""

import click

from knowde._feature import complete_proposition_client
from knowde._feature._shared.api.api_param import APIPath, APIQuery, NullPath
from knowde._feature._shared.api.endpoint import Endpoint, router2get
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_apifunc
from knowde._feature._shared.cli.field.model2click import model2decorator
from knowde.feature.deduction.domain import Deduction, StatsDeductions
from knowde.feature.deduction.dto import DeductionAddCLIParam, DeductionParam
from knowde.feature.deduction.repo.deduction import (
    complete_deduction_uid,
    deduct,
    list_deductions,
)

deduct_router = Endpoint.Deduction.create_router()
cf = ClientFactory(router=deduct_router, rettype=Deduction)

add_client = cf.post(
    NullPath(),
    to_apifunc(deduct, DeductionParam, Deduction),
    t_body=DeductionParam,
)
complete_uid = APIPath(name="", prefix="/completion").to_client(
    deduct_router,
    router2get,
    complete_deduction_uid,
    convert=lambda _res: click.echo(_res),
    query=APIQuery(name="pref_uid"),
)


getf = cf.replace(StatsDeductions)
list_client = getf.get(NullPath(), list_deductions)


@click.group("deduct")
def deduct_cli() -> None:
    """演繹."""


# @model2decorator(DeductionParam)
@deduct_cli.command("add")
@model2decorator(DeductionAddCLIParam)
def _add(**kwargs) -> None:  # noqa: ANN003
    """追加."""
    premises = [
        complete_proposition_client(pref_uid=pref_uid)
        for pref_uid in kwargs["premise_pref_uids"]
    ]
    conclusion = complete_proposition_client(pref_uid=kwargs["conclusion_pref_uid"])
    d = add_client(
        txt=kwargs["txt"],
        conclusion_id=conclusion.valid_uid,
        premise_ids=[p.valid_uid for p in premises],
        valid=kwargs["valid"],
    )
    click.echo("以下を作成しました")
    click.echo(d)
