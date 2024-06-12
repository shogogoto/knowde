from knowde._feature._shared.api.client_factory import ClientFactory, RouterConfig
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature.reference.domain import Reference
from knowde._feature.reference.repo.book import complete_ref

ref_router = Endpoint.Reference.create_router()
ref_factory = ClientFactory(router=ref_router, rettype=Reference)

complete_ref_client = ref_factory.to_get(
    RouterConfig().path("", "/completion").query("pref_uid"),
    complete_ref,
)
