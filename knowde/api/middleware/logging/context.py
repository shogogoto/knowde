"""async API用グローバル変数 = コンテキスト変数."""

import uuid
from contextvars import ContextVar
from typing import Final

request_id_var: Final[ContextVar[str | None]] = ContextVar("request_id", default=None)
user_id_var: Final[ContextVar[uuid.UUID | None]] = ContextVar("user_id", default=None)
