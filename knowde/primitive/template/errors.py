"""errors."""


class InvalidTemplateNameError(Exception):
    """テンプレート名にmarkが含まれる."""


class TemplateArgMismatchError(Exception):
    """テンプレート引数長が合わない."""


class TemplateUnusedArgError(Exception):
    """テンプレート引数が使われていない."""
