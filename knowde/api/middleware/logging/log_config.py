"""log設定."""

import logging
import sys
from typing import override

from .context import request_id_var, user_id_var


class Neo4jDeprecationWarningFilter(logging.Filter):
    """Filter out specific Neo4j deprecation warnings."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Allow record if it's not the specific deprecation warning."""
        msg = record.getMessage()
        suppress_msg = "CALL subquery without a variable scope clause is now deprecated"
        is_deprecation_warning = (
            record.name == "neo4j.notifications" and suppress_msg in msg
        )
        return not is_deprecation_warning


class ContextFilter(logging.Filter):
    """イベントIDやユーザーIDをログに含める."""

    @override
    def filter(self, record) -> bool:
        record.request_id = request_id_var.get() or "-"
        record.user_id = user_id_var.get() or "-"
        return True


def clear_logging() -> logging.Logger:
    """Remove any existing handlers."""
    logging.shutdown()
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    return root


def setup_logging() -> None:
    """fastapiログ用."""
    # Remove any existing handlers
    root_logger = clear_logging()

    # Create a handler and add the filter
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    handler.addFilter(Neo4jDeprecationWarningFilter())

    # Create a formatter with the request_id and user_id
    formatter = logging.Formatter(
        (
            "%(asctime)s.%(msecs)03d - %(levelname)s - "
            "[%(request_id)s] [%(user_id)s] - "
            "%(name)s - %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Configure uvicorn loggers to use the root logger's handlers
    for log_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        log = logging.getLogger(log_name)
        log.propagate = True
        log.handlers = []
