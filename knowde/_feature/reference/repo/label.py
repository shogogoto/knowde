from neomodel import RelationshipFrom

from knowde._feature._shared import LBase

LABEL_NAME = "Reference"
CLASS_NAME = f"L{LABEL_NAME}"


class LReference(LBase):
    __label__ = LABEL_NAME

    parent = RelationshipFrom(CLASS_NAME, "???")
