from pydantic_partial import create_partial_model

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
chooks.create_add("add", SentenceParam, None)

# for k, v in create_partial_model(SentenceParam).model_fields.items():
#     print(k, v, v.annotation)

chooks.create_change("ch", create_partial_model(SentenceParam), None)
