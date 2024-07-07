"""deduction interface."""

import click

from knowde._feature._shared.api.api_param import APIPath, APIQuery, NullPath
from knowde._feature._shared.api.endpoint import Endpoint, router2get
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_apifunc
from knowde.feature.deduction.domain import Deduction, StatsDeductions
from knowde.feature.deduction.dto import DeductionParam
from knowde.feature.deduction.repo.deduction import (
    complete_deduction_uid,
    deduct,
    list_deductions,
)

deduct_router = Endpoint.Deduction.create_router()
cf = ClientFactory(router=deduct_router, rettype=Deduction)

add_client = cf.post(NullPath(), to_apifunc(deduct, DeductionParam, Deduction))
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


@click.command("add")
# @model2decorator(DeductionParam)
def _add() -> None:
    """追加."""
