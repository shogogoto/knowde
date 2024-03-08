import click

from knowde._feature._shared import Endpoint
from knowde._feature._shared.api.client_factory import (
    APIClientFactory,
)
from knowde._feature._shared.cli.create_command import (
    set_add_change_command,
    set_basic_commands,
)
from knowde._feature.sentence.domain import SentenceParam

from .repo.label import SentenceUtil

s_router = Endpoint.Sentence.create_router()
factory = APIClientFactory(util=SentenceUtil, router=s_router)


@click.group("sentence")
def s_cli() -> None:
    pass


set_basic_commands(s_cli, factory)
set_add_change_command(s_cli, factory, SentenceParam)
