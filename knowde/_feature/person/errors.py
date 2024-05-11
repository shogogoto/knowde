from knowde._feature._shared.errors.errors import DomainError


class LifeDateInvalidError(DomainError):
    msg = "月が不明なのに日が分かるなどを許さない."
