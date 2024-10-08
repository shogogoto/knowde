"""本."""
from knowde.core.api.api_param import APIPath, APIQuery
from knowde.core.api.endpoint import Endpoint, router2get
from knowde.primitive.reference.domain import Reference
from knowde.primitive.reference.repo.book import complete_ref

ref_router = Endpoint.Reference.create_router()
complete_ref_client = APIPath(name="", prefix="/completion").to_client(
    ref_router,
    router2get,
    complete_ref,
    query=APIQuery(name="pref_uid"),
    convert=Reference.of,
)
