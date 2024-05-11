"""Rel Label."""
from neomodel import DateProperty

from knowde._feature._shared.repo.base import LBase


class RelWrite(LBase):
    """著す関係."""

    date = DateProperty()
