"""domain."""

from fastapi.security import APIKeyHeader

API_KEY_HEADER = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


# async def get_api_key(key: str = Security(api_key_header)) -> str:
#     """APIキーをヘッダーから取得・検証する."""
#     if key is not None and key == env.api_key:
#         return key
#     raise HTTPException(
#         status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
#     )
