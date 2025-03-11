"""root api."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neomodel import db

from knowde.complex.auth.routers import auth_router, user_router
from knowde.complex.entry.router import entry_router
from knowde.feature.api.middle import Neo4jTransactionMiddleware, neo4j_logger
from knowde.primitive.__core__ import ErrorHandlingMiddleware
from knowde.primitive.config.env import Settings
from knowde.tmp import deduct_router, def_router
from knowde.tmp.deduction.proposition import p_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
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
api.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(def_router)
api.include_router(p_router)
api.include_router(deduct_router)
api.include_router(auth_router)
api.include_router(user_router)
api.include_router(entry_router)


@api.get("/health")
async def check_health() -> str:
    """Check health."""
    return "ok"
