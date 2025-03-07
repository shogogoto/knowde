"""auth errors."""


class TokenUnsavedError(Exception):
    """認証用トークンが保存されていない."""


class UnauthorizedError(Exception):
    """認証失敗."""
