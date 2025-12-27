"""テスト用認証etc."""

from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient

from knowde.api import api
from knowde.config.env import Settings
from knowde.shared.user.label import LUser


async def async_client() -> AsyncGenerator[AsyncClient]:  # noqa: D103
    s = Settings()
    async with AsyncClient(
        transport=ASGITransport(app=api),
        base_url=s.KNOWDE_URL,
    ) as client:
        yield client


_PW = "password"


async def async_auth_header(email="one@gmail.com") -> dict[str, str]:  # noqa: D103
    await aregister(email)
    return await aauth_header(email)


async def aregister(email="one@gmail.com") -> LUser:  # noqa: D103
    async for ac in async_client():
        d = {"email": email, "password": _PW}
        await ac.post("/auth/register", json=d)
    return await LUser.nodes.get(email=email)


async def aauth_header(email="one@gmail.com") -> dict[str, str]:  # noqa: D103
    async for ac in async_client():
        d = {"username": email, "password": _PW}
        res = await ac.post("/auth/jwt/login", data=d)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    msg = "async_auth_header"
    raise AssertionError(msg)  # 到達しないはず
