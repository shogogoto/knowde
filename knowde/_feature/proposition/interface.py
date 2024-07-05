# proposition
from uuid import UUID

from knowde._feature._shared.api.api_param import APIPath, APIQuery, NullPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_apifunc
from knowde._feature.proposition.domain import Proposition
from knowde._feature.proposition.repo.repo import (
    add_proposition,
    change_proposition,
    complete_proposition,
    delete_proposition,
    list_propositions,
)
from knowde.feature.deduction.dto import PropositionParam

p_router = Endpoint.Proposition.create_router()
pf = ClientFactory(router=p_router, rettype=Proposition)

add_client = pf.post(NullPath(), add_proposition, t_body=PropositionParam)
complete_client = pf.get(
    APIPath(name="", prefix="/completion"),
    complete_proposition,
    query=APIQuery(name="pref_uid"),
)
pid = APIPath(name="uid", prefix="")
_change = to_apifunc(
    change_proposition,
    PropositionParam,
    Proposition,
    ignores=[("uid", UUID)],
)
change_client = pf.put(pid, _change, t_body=PropositionParam)
delete_client = pf.delete(pid, delete_proposition)
list_client = pf.gets(NullPath(), list_propositions)
