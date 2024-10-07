"""Tree Leaf変換=Tranformerと変換後型."""


from lark.visitors import TransformerChain

from .context import TContext
from .heading import THeading
from .source_about import TSourceAbout
from .statement import TStatemet


def common_transformer() -> TransformerChain:
    """パースに使用するTransformer一式."""
    return THeading() * TSourceAbout() * TStatemet() * TContext()
