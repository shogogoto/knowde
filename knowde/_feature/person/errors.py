from knowde._feature._shared.errors.errors import DomainError


class UnclearLifeDateError(DomainError):
    msg = "月が不明なのに日が分かるなどを許さない."
