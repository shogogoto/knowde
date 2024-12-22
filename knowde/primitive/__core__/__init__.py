# ruff: noqa
"""グローバルに使用される基本機能."""

import os

from neomodel import config

from .api import *  # noqa: F403
from .cli import *  # noqa: F403
from .domain import Entity  # noqa: F401
from .errors import *  # noqa: F403
from .label_repo import *  # noqa: F403
from .timeutil import TZ, jst_now, to_date  # noqa: F401
from .types import NeoModel, NXGraph  # noqa: F401
from .typeutil import *  # noqa: F403
from .nxutil import *

config.DATABASE_URL = os.environ["NEO4J_URL"]
