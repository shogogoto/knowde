"""independent features shared modules."""

import os

from neomodel import config

from .endpoint import Endpoint  # noqa: F401
from .timeutil import TZ, jst_now  # noqa: F401

config.DATABASE_URL = os.environ["NEO4J_URL"]
