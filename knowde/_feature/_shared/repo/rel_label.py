from neomodel import IntegerProperty

from knowde._feature._shared.repo.base import RelBase


class RelOrder(RelBase):
    order = IntegerProperty()
