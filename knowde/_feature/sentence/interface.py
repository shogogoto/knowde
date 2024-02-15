import click

from knowde._feature._shared import Endpoint
from knowde._feature._shared.api.client_factory import (
    create_add_client_factory,
    create_basic_clients,
    create_change_client_factory,
)
from knowde._feature._shared.cli.create_group import rm_clifunc
from knowde._feature.sentence.domain import SentenceParam

from .repo.label import s_util

s_router = Endpoint.Sentence.create_router()
clients = create_basic_clients(s_util, s_router)
add_f = create_add_client_factory(s_util, s_router)
ch_f = create_change_client_factory(s_util, s_router, clients.complete)

add_client = add_f(SentenceParam)
ch_client = ch_f(SentenceParam)


@click.group("sentence")
def s_cli() -> None:
    pass


# s_cli.add_command(to_command("ls", view_options(clients.ls), "help!"))
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
