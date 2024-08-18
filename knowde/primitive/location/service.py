"""application service."""
from uuid import UUID

from knowde.primitive.location.dto import LocationDetailView
from knowde.primitive.location.repo.repo import find_location_tree


def detail_location_service(uid: UUID) -> LocationDetailView:
    """直接Genericを返す."""
    tree = find_location_tree(uid)
    return LocationDetailView(detail=tree.build())
