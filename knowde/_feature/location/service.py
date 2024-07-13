from uuid import UUID

from knowde._feature.location.dto import LocationDetailView
from knowde._feature.location.repo.repo import find_location_tree


def detail_location_service(uid: UUID) -> LocationDetailView:
    return LocationDetailView(detail=find_location_tree(uid).build())
