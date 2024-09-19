"""test source parsing."""
from datetime import date

import pytest

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.source.domain import SourceMismatchError, SourceTree
from knowde.feature.parser.domain.testing import echo_tree

_s = r"""
    # source1
        @author tanaka tarou
        @published 2020-11-11
        xxx
    ## 2.1
        ! multiline
    ### 3.1
        ! define
        xxx
    #### 4.1
    ##### 5.1
    ###### 6.1
    ### 3. dedent
    ### 3. same level
    ### 3. same level
    # source2
    other tree line
        hhh
    !C2
"""


def test_source_about() -> None:
    """情報源について."""
    t = transparse(_s)
    echo_tree(t)
    s1 = SourceTree.create(t, "source1")
    assert s1.about.tuple == ("source1", "tanaka tarou", date(2020, 11, 11))
    s2 = SourceTree.create(t, "source2")
    assert s2.about.tuple == ("source2", None, None)
    with pytest.raises(SourceMismatchError):
        SourceTree.create(t, "source")
    with pytest.raises(SourceMismatchError):
        SourceTree.create(t, "xxx")


def test_source_tree() -> None:
    """見出しの階層構造を取得."""
