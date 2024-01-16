from knowde._feature._shared import Endpoint, create_group, set_basic_router
from knowde._feature._shared.api.set_basic_router import create_router
from knowde._feature.sentence.domain import Sentence, SentenceParam

from .repo.label import s_util

s_router, hooks = set_basic_router(
    s_util,
    create_router(Endpoint.Sentence),
)
hooks.create_add(SentenceParam)
hooks.create_change(SentenceParam)

s_cli, chooks = create_group(
    "sentence",
    Endpoint.Sentence,
    t_model=Sentence,
)
chooks.create_add("add", SentenceParam)
chooks.create_change("ch", SentenceParam)
chooks.create_rm("rm")
chooks.create_ls("ls")
