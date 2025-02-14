"""command implementation."""
import threading
import webbrowser

import uvicorn
from fastapi import FastAPI

from knowde.feature.__core__.config import Settings
from knowde.feature.auth.domain import response_queue
from knowde.feature.auth.sso.route import GoogleSSOResponse, router_google_sso


def run_server(port: int) -> None:
    """FastAPIサーバーを実行."""
    app = FastAPI()
    app.include_router(router_google_sso(port))
    uvicorn.run(app, host="localhost", port=port)


def browse_for_sso() -> GoogleSSOResponse:
    """ブラウザを開いてSSOアカウントのレスポンスを取得."""
    port = Settings().SSO_PROT
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    webbrowser.open(f"http://localhost:{port}/google/login")
    return response_queue().get()


def sign_up_proc() -> None:
    """アカウント登録."""
    s = Settings()
    _res = s.post("/auth/register", json={""})
