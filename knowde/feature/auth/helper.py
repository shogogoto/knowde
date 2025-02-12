"""helper."""
import webbrowser

from aiohttp import web
from aiohttp.typedefs import Handler

from knowde.feature.auth import google_sso


async def start_local_server(callback: Handler) -> web.AppRunner:
    """Try."""
    app = web.Application()
    app.router.add_get("/google/callback", callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8000)
    await site.start()
    return runner


async def handle_callback(request: web.Request) -> web.Response:
    """Store the auth code from the callback."""
    query_params = request.query
    _auth_code = query_params.get("code")
    return web.Response(
        text="認証が完了しました。このウィンドウを閉じて、CLIに戻ってください。",
    )


async def authenticate() -> None:
    """Try."""
    # webbrowser.open(auth_url)
    sso = google_sso()
    runner = await start_local_server(handle_callback)
    try:
        async with sso:
            _redirect = await sso.get_login_redirect()
            webbrowser.open(str(sso.redirect_uri))
            # webbrowser.open(auth_url)
            # while self.user_info is None:
            #     await asyncio.sleep(1)
            # return self.user_info
    finally:
        await runner.cleanup()
