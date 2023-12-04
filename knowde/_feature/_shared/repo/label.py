from neomodel import DateTimeProperty, StringProperty, StructuredNode, UniqueIdProperty

from knowde._feature._shared.timeutil import jst_now


class LBase(StructuredNode):
    __abstract_node__ = True
    uid = UniqueIdProperty()
    name = StringProperty()
    created = DateTimeProperty()
    updated = DateTimeProperty()

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now
