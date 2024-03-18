"""independent features shared modules."""

import os

from neomodel import config

from .api import *  # noqa: F403
from .cli import *  # noqa: F403
from .domain import DomainModel  # noqa: F401
from .errors import *  # noqa: F403
from .repo import *  # noqa: F403
from .types import NeoModel, NXGraph  # noqa: F401

config.DATABASE_URL = os.environ["NEO4J_URL"]
