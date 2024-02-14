from knowde._feature._shared import Endpoint, create_group, set_basic_router
from knowde._feature._shared.integrated_interface.generate_req import APIRequests
from knowde._feature.sentence.domain import Sentence, SentenceParam

from .repo.label import s_util

s_router, reqs, add_and_change = set_basic_router(
    s_util,
    Endpoint.Sentence.create_router(),
)
add_and_change(SentenceParam)

s_cli, chooks = create_group(
    "sentence",
    Endpoint.Sentence,
    t_model=Sentence,
)
chooks.create_add("add", SentenceParam)
chooks.create_change("ch", SentenceParam)
chooks.create_rm("rm")
chooks.create_ls("ls")

s_router = Endpoint.Sentence.create_router()
reqs = APIRequests(router=s_router)

# reqs.post()
