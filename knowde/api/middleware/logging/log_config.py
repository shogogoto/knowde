"""log設定."""

import logging
import sys
from typing import override

from pythonjsonlogger.json import JsonFormatter

from knowde.config.env import Settings

from .context import method_var, request_id_var, url_var, user_id_var


class Neo4jDeprecationWarningFilter(logging.Filter):
    """Filter out specific Neo4j deprecation warnings."""

    @override
    def filter(self, record):
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
    def filter(self, record):
        record.request_id = request_id_var.get() or "-"
        record.user_id = user_id_var.get() or "-"
        record.url = url_var.get() or "-"
        record.method = method_var.get() or "-"
        return True


def clear_logging() -> logging.Logger:
    """Remove any existing handlers."""
    logging.shutdown()
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.setLevel(logging.WARNING)  # defaultに戻す
    return root


_datefmt = "%Y-%m-%d %H:%M:%S"


def json_formatter() -> logging.Formatter:
    """Log formatter for JSON."""
    # The fields to include in the JSON log.
    format_str = (
        "%(asctime)s %(msecs)03d %(levelname)s "
        "%(request_id)s %(user_id)s %(method)s %(url)s "
        "%(name)s %(lineno) %(message)s"
    )
    return JsonFormatter(format_str, datefmt=_datefmt)


def text_formatter() -> logging.Formatter:
    """Log formatter for line."""
    return logging.Formatter(
        (
            "%(asctime)s.%(msecs)03d [%(levelname)-8s] "
            "(%(request_id)s %(user_id)s %(method)s %(url)s) "
            "%(name)s %(lineno)s: %(message)s"
        ),
        datefmt=_datefmt,
    )


s = Settings()


def setup_logging() -> None:
    """fastapiログ用."""
    root_logger = clear_logging()
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())
    handler.addFilter(Neo4jDeprecationWarningFilter())
    if s.LOGGING_FORMAT == "json":
        handler.setFormatter(json_formatter())
    else:
        handler.setFormatter(text_formatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(s.LOGGING_LEVEL)
