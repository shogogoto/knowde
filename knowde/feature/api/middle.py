"""custom middleware."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request, Response, status
from neomodel import db
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing_extensions import override


class Neo4jTransactionMiddleware(BaseHTTPMiddleware):
    """API失敗時にロールバック."""

    @override
    def __init__(
        self,
        app: FastAPI,
        paths: list[str] | None = None,  # トランザクション管理を適用するパスのリスト
        exclude_paths: list[str] | None = None,  # 除外するパスのリスト
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(app)
        self.paths = paths or []
        self.exclude_paths = exclude_paths or []
        self.logger = logger or logging.getLogger(__name__)

    @override
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # パスが除外リストに含まれている場合はトランザクション管理をスキップ
        if self._should_skip(request.url.path):
            return await call_next(request)

        # トランザクション開始
        db.begin()
        try:
            # リクエスト処理
            res = await call_next(request)
            if status.HTTP_200_OK <= res.status_code < status.HTTP_300_MULTIPLE_CHOICES:
                db.commit()
            else:
                db.rollback()
                self.logger.warning(
                    "Transaction rolled back due to response status %s",
                    res.status_code,
                )
        except Exception:
            db.rollback()
            logging.exception("Transaction rolled back due to error")
            raise
        return res

    def _should_skip(self, path: str) -> bool:
        """トランザクション管理をスキップすべきかどうかを判定."""
        # 除外パスに含まれている場合はスキップ
        if any(path.startswith(exclude_path) for exclude_path in self.exclude_paths):
            return True
        # パスが指定されている場合、該当するパスのみ処理
        if self.paths and not any(path.startswith(route) for route in self.paths):
            return True
        return False


def neo4j_logger() -> logging.Logger:
    """カスタムロガーの設定例."""
    logger = logging.getLogger("neo4j_transaction")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    )
    logger.addHandler(handler)
    return logger
