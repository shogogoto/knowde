class APIParamBindError(Exception):
    """kwargsからRequestMethodへの値渡しに失敗."""


class PostFailureError(Exception):
    """postに失敗."""


class PutFailureError(Exception):
    """putに失敗."""


class GetFailureError(Exception):
    """getに失敗."""


class DeleteFailureError(Exception):
    """deleteに失敗."""
