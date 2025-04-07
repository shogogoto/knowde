"""repo."""

from collections.abc import Generator
from contextlib import contextmanager

from pydantic import BaseModel, PrivateAttr

from knowde.complex.entry import NameSpace
from knowde.complex.entry.category.folder.repo import fetch_namespace
from knowde.complex.entry.label import LFolder
from knowde.complex.entry.namespace import fill_parents
from knowde.primitive.user.repo import LUser


# fsと独
class NameSpaceRepo(BaseModel, arbitrary_types_allowed=True):
    """user namespace."""

    user: LUser
    _ns: NameSpace | None = PrivateAttr(default=None)

    @contextmanager
    def ns_scope(self) -> Generator[NameSpace]:
        """何度もfetchしたくない."""  # noqa: DOC402
        ns = fetch_namespace(self.user.uid)
        try:
            self._ns = ns
            yield ns
        finally:
            self._ns = None

    def add_folders(self, *names: str) -> LFolder:
        """Return tail folder."""
        if self._ns is not None:
            return fill_parents(self._ns, *names)
        with self.ns_scope() as ns:
            return fill_parents(ns, *names)
