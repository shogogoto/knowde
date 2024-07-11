"""timeline interface."""
from knowde._feature._shared.api.api_param import NullPath
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature._shared.api.facade import ClientFactory
from knowde._feature._shared.api.paramfunc import to_apifunc
from knowde._feature.timeline.domain.domain import TimeValue
from knowde._feature.timeline.interface.dto import TimelineAddParam
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.service import list_time_service

tl_router = Endpoint.Timeline.create_router()
cf = ClientFactory(router=tl_router, rettype=TimeValue)

add_client = cf.post(
    NullPath(),
    to_apifunc(fetch_time, TimelineAddParam, convert=lambda x: x.value),
)

list_client = cf.gets(NullPath(), list_time_service)
