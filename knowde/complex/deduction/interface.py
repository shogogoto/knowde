"""deduction interface."""
from __future__ import annotations

from uuid import UUID

import click

from knowde._feature import complete_proposition_client
from knowde.complex.deduction.domain import Deduction, StatsDeductions
from knowde.complex.deduction.dto import (
    DeductionAddCLIParam,
    DeductionParam,
    ReplaceConclusionAPIParam,
    ReplaceConclusionCLIParam,
    ReplacePremisesAPIParam,
    ReplacePremisesCLIParam,
)
from knowde.complex.deduction.repo.deduction import (
    complete_deduction_mapper,
    deduct,
    list_deductions,
    remove_deduction,
    replace_conclusion,
    replace_premises,
)
from knowde.complex.deduction.repo.label import DeductionMapper
from knowde.core.api.api_param import APIPath, APIQuery, NullPath
from knowde.core.api.endpoint import Endpoint, router2get
from knowde.core.api.facade import ClientFactory
from knowde.core.api.paramfunc import to_bodyfunc
from knowde.core.cli.click_decorators import each_args
from knowde.core.cli.field.model2click import model2decorator

deduct_router = Endpoint.Deduction.create_router()
cf = ClientFactory(router=deduct_router, rettype=Deduction)

add_client = cf.post(
    NullPath(),
    to_bodyfunc(deduct, DeductionParam, Deduction),
    t_body=DeductionParam,
)
complete_mapper = APIPath(name="", prefix="/completion").to_client(
    deduct_router,
    router2get,
    complete_deduction_mapper,
    convert=DeductionMapper.of,
    query=APIQuery(name="pref_uid"),
)

pp = APIPath(name="uid", prefix="")
getf = ClientFactory(router=deduct_router, rettype=StatsDeductions)
list_client = getf.get(NullPath(), list_deductions)
delete_client = cf.delete(pp, remove_deduction)
repl_p_client = cf.put(
    pp.add(prefix="premises"),
    to_bodyfunc(
        replace_premises,
        ReplacePremisesAPIParam,
        Deduction,
        ignores=[("uid", UUID)],
    ),
    t_body=ReplacePremisesAPIParam,
)

repl_c_client = cf.put(
    pp.add(prefix="conclusion"),
    to_bodyfunc(
        replace_conclusion,
        ReplaceConclusionAPIParam,
        Deduction,
        ignores=[("uid", UUID)],
    ),
    t_body=ReplaceConclusionAPIParam,
)


@click.group("deduct")
def deduct_cli() -> None:
    """演繹."""


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
    click.echo(d.output)


@deduct_cli.command("ls")
def _ls() -> None:
    """一覧."""
    ds = list_client()
    for d in ds.values:
        click.echo(d.output)


@deduct_cli.command("rm")
@each_args(
    "pref_uids",
    converter=lambda pref_uid: complete_deduction_mapper(pref_uid=pref_uid),
)
def _rm(m: DeductionMapper) -> None:
    """削除."""
    delete_client(uid=m.valid_uid)
    click.echo(f"{m}を削除しました")


@deduct_cli.command("repl_p")
@model2decorator(ReplacePremisesCLIParam)
def _repl_p(
    deduction_pref_uid: str,
    premise_pref_uids: list[str],
) -> None:
    """前提の置換."""
    m = complete_deduction_mapper(pref_uid=deduction_pref_uid)
    premises = [complete_proposition_client(pref_uid=pid) for pid in premise_pref_uids]
    d = repl_p_client(
        uid=m.valid_uid,
        premise_uids=[p.valid_uid for p in premises],
    )
    click.echo("前提を置換しました")
    click.echo(d.output)


@deduct_cli.command("repl_c")
@model2decorator(ReplaceConclusionCLIParam)
def _repl_c(
    deduction_pref_uid: str,
    conclusion_pref_uid: str,
) -> None:
    """結論の置換."""
    m = complete_deduction_mapper(pref_uid=deduction_pref_uid)
    c = complete_proposition_client(pref_uid=conclusion_pref_uid)
    # d = replace_conclusion(m.valid_uid, c.valid_uid)
    d = repl_c_client(uid=m.valid_uid, conclusion_uid=c.valid_uid)
    click.echo("結論を置換しました")
    click.echo(d.output)
