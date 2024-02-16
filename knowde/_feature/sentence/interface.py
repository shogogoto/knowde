import click

from knowde._feature._shared import Endpoint
from knowde._feature._shared.api.client_factory import (
    APIClientFactory,
)
from knowde._feature._shared.cli.click_decorators.view.options import view_options
from knowde._feature._shared.cli.create_group import rm_clifunc
from knowde._feature.sentence.domain import SentenceParam

from .repo.label import s_util

s_router = Endpoint.Sentence.create_router()
factory = APIClientFactory(util=s_util, router=s_router)
clients = factory.create_basics()
add = factory.create_add(SentenceParam)
ch = factory.create_change(SentenceParam)


@click.group("sentence")
def s_cli() -> None:
    pass


s_cli.add_command(
    click.command("ls", help="help!")(
        view_options(clients.ls),
    ),
)
s_cli.add_command(
    click.command(help="rm help")(
        rm_clifunc(clients.rm, clients.complete),
    ),
)
# )
# chooks.create_add("add", SentenceParam)
# chooks.create_change("ch", SentenceParam)
# chooks.create_rm("rm")
# chooks.create_ls("ls")
