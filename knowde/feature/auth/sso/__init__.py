"""single sign on."""
from __future__ import annotations

from enum import Enum


class Provider(Enum):
    """Single Sign on provider."""

    GOOGLE = "google"
