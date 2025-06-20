"""root api."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neomodel import db

from knowde.complex.auth.routers import auth_router, user_router
from knowde.complex.entry.router import entry_router
from knowde.complex.nxdb.router import nxdb_router
from knowde.feature.api.middle import (
    Neo4jTransactionMiddleware,
    neo4j_logger,
    set_error_handlers,
)
from knowde.feature.knowde.router import knowde_router
from knowde.feature.webhook.routers import webhook_router
from knowde.primitive.__core__ import ErrorHandlingMiddleware
from knowde.primitive.config.env import Settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:  # noqa: RUF029
    """Set up DB etc."""
    s = Settings()
    s.setup_db()
    db.install_all_labels()
    yield
    s.terdown_db()


api = FastAPI(lifespan=lifespan)
api.add_middleware(ErrorHandlingMiddleware)
api.add_middleware(
    Neo4jTransactionMiddleware,
    # paths=["/api/v1"], 適用パス
    exclude_paths=["/health"],
    logger=neo4j_logger(),
)
s = Settings()
api.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=s.allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_error_handlers(api)


api.include_router(auth_router)
api.include_router(user_router)
api.include_router(entry_router())
api.include_router(nxdb_router())
api.include_router(knowde_router())
api.include_router(webhook_router())


def root_router() -> FastAPI:  # noqa: D103
    return api


@api.get("/health")
async def check_health() -> str:
    """Check health."""
    return "ok"
