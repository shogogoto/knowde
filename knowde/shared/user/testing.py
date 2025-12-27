"""テスト用認証etc."""

from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient

from knowde.api import api
from knowde.config.env import Settings


async def async_client() -> AsyncGenerator[AsyncClient]:  # noqa: D103
    s = Settings()
    async with AsyncClient(
        transport=ASGITransport(app=api),
        base_url=s.KNOWDE_URL,
    ) as client:
        yield client


async def async_auth_header() -> dict[str, str]:  # noqa: D103
    async for ac in async_client():
        email = "one@gmail.com"
        password = "password"  # noqa: S105
        d = {"email": email, "password": password}
        res = await ac.post("/auth/register", json=d)
        d = {"username": email, "password": password}
        res = await ac.post("/auth/jwt/login", data=d)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    msg = "async_auth_header"
    raise AssertionError(msg)  # 到達しないはず
