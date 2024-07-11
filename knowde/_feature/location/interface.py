from knowde._feature._shared.api.const import CmplPath, CmplQ
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_queryfunc
from knowde._feature.location.domain import Location
from knowde._feature.location.repo.label import LocUtil

loc_router = Endpoint.Location.create_router()
cf = ClientFactory(router=loc_router, rettype=Location)

complete_clinet = cf.get(
    CmplPath,
    to_queryfunc(
        LocUtil.complete,
        [str],
        Location,
        lambda x: x.to_model(),
    ),
    query=CmplQ,
)
