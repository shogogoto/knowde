from knowde._feature.person.domain import AuthorParam
from knowde._feature.person.repo.label import AuthorUtil


def add_author(p: AuthorParam) -> None:
    """同姓同名はあり得るので特に制約はなし."""
    AuthorUtil.create(name=p.name)
