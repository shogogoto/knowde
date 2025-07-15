"""log設定."""

import logging
import sys
from typing import override

from pythonjsonlogger.json import JsonFormatter

from .context import request_id_var, url_var, user_id_var


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
        record.url = url_var.get() or "-"
        return True


def clear_logging() -> logging.Logger:
    """Remove any existing handlers."""
    logging.shutdown()
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.setLevel(logging.WARNING)  # defaultに戻す
    return root


def log_formatter() -> logging.Formatter:
    """Log formatter for JSON."""
    # The fields to include in the JSON log.
    format_str = (
        "%(asctime)s %(msecs)03d %(levelname)s %(name)s "
        "%(request_id)s %(url)s %(user_id)s %(message)s"
    )
    return JsonFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging() -> None:
    """fastapiログ用."""
    root_logger = clear_logging()
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    handler.addFilter(Neo4jDeprecationWarningFilter())
    handler.setFormatter(log_formatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Configure uvicorn loggers to use the root logger's handlers
    for log_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        log = logging.getLogger(log_name)
        log.propagate = True
        log.handlers = []

    # knowde以下のロガーがルートに伝播するようにする
    knowde_logger = logging.getLogger("knowde")
    knowde_logger.propagate = True
    knowde_logger.handlers = []
