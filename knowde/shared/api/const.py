"""API定義用のよく使うものを定数化."""

from knowde.shared.api.api_param import APIPath, APIQuery

CmplPath = APIPath(name="", prefix="/completion")
UUIDPath = APIPath(name="uid", prefix="")
CmplQ = APIQuery(name="pref_uid")
