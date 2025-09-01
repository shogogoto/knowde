"""root api."""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neomodel.async_.core import AsyncDatabase

from knowde.api.middleware.error_handling import ErrorHandlingMiddleware
from knowde.api.middleware.logging import LoggingMiddleware
from knowde.api.middleware.logging.log_config import setup_logging
from knowde.api.middleware.transaction import Neo4jTransactionMiddleware
from knowde.config.env import Settings
from knowde.feature.entry.resource.repo.router import nxdb_router
from knowde.feature.entry.router import entry_router
from knowde.feature.knowde.router import knowde_router
from knowde.feature.user.routers import auth_router, user_router

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


s = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """Set up DB etc."""
    s.setup_db()
    await AsyncDatabase().install_all_labels()
    yield
    await AsyncDatabase().close_connection()


api = FastAPI(lifespan=lifespan)

api.add_middleware(ErrorHandlingMiddleware)
api.add_middleware(
    Neo4jTransactionMiddleware,
    # paths=["/api/v1"], 適用パス
)
api.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=s.allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.add_middleware(LoggingMiddleware)

api.include_router(auth_router())
api.include_router(user_router())
api.include_router(entry_router())
api.include_router(nxdb_router())
api.include_router(knowde_router())


def is_pytest_running() -> bool:  # noqa: D103
    return "pytest" in sys.modules


if not is_pytest_running():
    setup_logging()


def root_router() -> FastAPI:  # noqa: D103
    return api


@api.get("/health")
async def check_health() -> str:
    """Check health."""
    return "ok"
