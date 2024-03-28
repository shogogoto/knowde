"""referenceとpersonに依存."""
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature.person.label import AuthorUtil, LAuthor
from knowde._feature.reference.repo.label import BookUtil, LBook
from knowde.feature.reference.domain import BookParam

RelAuthorUtil = RelUtil(
    t_source=LAuthor,
    t_target=LBook,
    name="WRITE",
)


def add_book(p: BookParam) -> None:
    """Register book reference."""
    book = BookUtil.create(title=p.title)
    if p.author_name is not None:
        author = AuthorUtil.find_one_or_none(name=p.author_name)
        if author is None:
            author = AuthorUtil.create(name=p.author_name)
        RelAuthorUtil.connect(author.label, book.label)
