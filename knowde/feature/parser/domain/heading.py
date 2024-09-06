"""textから章節を抜き出す."""
from __future__ import annotations

from lark import Token, Transformer, Tree
from networkx import DiGraph
from pydantic import BaseModel, Field
from typing_extensions import override

from knowde.core.types import NXGraph  # noqa: TCH001
from knowde.feature.parser.domain.parser import CommonVisitor


class Heading(BaseModel, frozen=True):
    """見出しまたは章節."""

    value: str
    level: int = Field(ge=1, le=6)

    def __str__(self) -> str:
        """For user string."""
        return f"h{self.level}={self.value}"


class THeading(Transformer):
    """heading transformer."""

    def _common(self, tok: Token, level: int) -> Heading:
        return Heading(value=tok.replace("#", "").strip(), level=level)

    def H1(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H1."""
        return self._common(tok, 1)

    def H2(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H2."""
        return self._common(tok, 2)

    def H3(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H3."""
        return self._common(tok, 3)

    def H4(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H4."""
        return self._common(tok, 4)

    def H5(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H5."""
        return self._common(tok, 5)

    def H6(self, tok: Token) -> Heading:  # noqa: N802
        """Markdown H6."""
        return self._common(tok, 6)


class HeadingTree(BaseModel, frozen=True):
    """見出しの階層."""

    g: NXGraph

    @property
    def nodes(self) -> set[Heading]:
        """Heading nodes."""
        return set(self.g.nodes)

    @property
    def count(self) -> int:
        """Total number of heading."""
        return len(self.nodes)

    def get(self, title: str) -> Heading:
        """見出しを特定."""
        _f = list(filter(lambda x: title in x.value, self.nodes))
        if len(_f) == 0:
            msg = f"{title}を含む見出しはありません"
            raise KeyError(msg)
        if len(_f) > 1:
            msg = f"{title}を含む見出しが複数見つかりました"
            raise KeyError(msg)
        return _f[0]

    def info(self, title: str) -> tuple[int, int]:
        """Return level and Count children for test."""
        h = self.get(title)
        children = self.g[h]
        return (h.level, len(children))


class HeadingVisitor(BaseModel, CommonVisitor):
    """見出しのツリー."""

    g: NXGraph = Field(default_factory=DiGraph)

    @property
    def tree(self) -> HeadingTree:
        """To tree."""
        return HeadingTree(g=self.g)

    @override
    def do(self, tree: Tree) -> None:
        tgt = tree.children[0]
        self.g.add_node(tgt)
        subtrees = filter(lambda x: isinstance(x, Tree), tree.children)
        for t in subtrees:
            for c in t.children:
                self.g.add_edge(tgt, c)
