"""Rel Label."""
from neomodel import DateProperty

from knowde.core.repo.base import LBase


class RelWrite(LBase):
    """著す関係."""

    date = DateProperty()
