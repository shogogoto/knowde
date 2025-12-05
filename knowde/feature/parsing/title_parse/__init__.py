"""txtからtitleだけを取得する.

いちいちテキスト全てをparseしてtree, graphに変換するのが重い
それを回避したい
"""

from knowde.shared.errors import DomainError


class NonTitleError(DomainError):
    """タイトルが見つからない."""


def title_parse(text: str) -> str:
    """txtからtitleだけを取得する.

    Args:
        text: markdown text.

    Returns:
        The first line of title.

    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped

    raise NonTitleError
