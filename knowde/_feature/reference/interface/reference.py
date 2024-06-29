from knowde._feature._shared.api.api_param import APIPath, APIQuery
from knowde._feature._shared.api.endpoint import Endpoint, router2get
from knowde._feature.reference.domain import Reference
from knowde._feature.reference.repo.book import complete_ref

ref_router = Endpoint.Reference.create_router()
complete_ref_client = APIPath(name="", prefix="/completion").to_client(
    ref_router,
    router2get,
    complete_ref,
    apiquery=APIQuery(name="pref_uid"),
    convert=Reference.of,
)
