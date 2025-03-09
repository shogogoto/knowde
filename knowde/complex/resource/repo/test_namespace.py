"""test repo."""


from knowde.complex.resource import ResourceMeta
from knowde.complex.resource.repo import SyncResourceMeta, sync_namespace
from knowde.primitive.user.repo import LUser


def test_add_namespace() -> None:
    """新規追加."""
    user = LUser().save()
    meta = SyncResourceMeta([])
    meta.root.append(ResourceMeta(title="# title"))

    _ns = sync_namespace(user.uid, meta)
