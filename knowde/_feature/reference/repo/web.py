from uuid import UUID

from knowde._feature.reference.domain import Web
from knowde._feature.reference.dto import PartialWebParam, WebParam
from knowde._feature.reference.repo.label import WebUtil
from knowde.core.errors.domain import AlreadyExistsError


def add_webref(p: WebParam) -> Web:
    """Web Referenceの追加."""
    if WebUtil.find_one_or_none(title=p.title):
        msg = f"「{p.title}」は既に登録済みです."
        raise AlreadyExistsError(msg)
    return WebUtil.create(**p.model_dump()).to_model()


def change_web(ref_uid: UUID, p: PartialWebParam) -> Web:
    return WebUtil.change(uid=ref_uid, **p.model_dump()).to_model()
