"""errors."""


class InvalidTemplateNameError(Exception):
    """テンプレート名にmarkが含まれる."""


class TemplateArgMismatchError(Exception):
    """テンプレート引数長が合わない."""


class TemplateUnusedArgError(Exception):
    """テンプレート引数が使われていない."""


class TemplateConflictError(Exception):
    """テンプレート名の衝突."""


class TemplateNotFoundError(Exception):
    """テンプレート一覧が存在しない."""
