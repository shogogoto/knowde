

from knowde._feature._shared.api.client_factory import ClientFactory, RouterConfig
from knowde._feature._shared.api.endpoint import Endpoint
from knowde._feature.reference.domain import Section
from knowde._feature.reference.dto import HeadlineParam
from knowde._feature.reference.repo.section import (
    add_section,
    change_section,
    remove_section,
)

sec_router = Endpoint.Chapter.create_router()
factory = ClientFactory(router=sec_router, rettype=Section)

add_client = factory.to_post(
    RouterConfig().path("chap_uid").body(HeadlineParam),
    add_section,
)

change_client = factory.to_put(
    RouterConfig().path("sec_uid").body(HeadlineParam),
    change_section,
)

remove_client = factory.to_delete(
    RouterConfig().path("chap_uid"),
    remove_section,
)


# complete_client = factory.to_get(
#     RouterConfig().path("", "/completion").query("pref_uid"),
#     complete_chapter,
# )


# @click.group("section")
# def sec_cli() -> None:
#     """節に関するコマンド群."""


# @sec_cli.command("add")
# @model2decorator(HeadlineParam)
# def add(chap_uid: UUID, **kwargs) -> None:
#     s = add_client(chap_uid=chap_uid, **kwargs)
