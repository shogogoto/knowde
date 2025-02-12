"""auth cli."""

import threading
import webbrowser

import click
import uvicorn
from fastapi import FastAPI

from knowde.feature.__core__.config import Settings, response_queue

from . import auth_router


def run_server(port: int) -> None:
    """FastAPIサーバーを実行."""
    app = FastAPI()
    app.include_router(auth_router)
    uvicorn.run(app, host="localhost", port=port)


@click.command("login")
def login_cmd() -> None:
    """Login."""
    s = Settings()
    port = s.PORT
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    webbrowser.open(f"http://localhost:{port}/google/login")
    _response = response_queue().get()
