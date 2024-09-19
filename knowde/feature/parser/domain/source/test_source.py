"""test source parsing."""
from datetime import date

import pytest

from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.parser.transfomer.heading import Heading
from knowde.feature.parser.domain.source.domain import SourceMismatchError, SourceTree

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
    s1 = SourceTree.create(t, "source1")
    assert s1.about.tuple == ("source1", "tanaka tarou", date(2020, 11, 11))
    s2 = SourceTree.create(t, "source2")
    assert s2.about.tuple == ("source2", None, None)
    with pytest.raises(SourceMismatchError):
        SourceTree.create(t, "source")
    with pytest.raises(SourceMismatchError):
        SourceTree.create(t, "xxx")


def test_heading_children() -> None:
    """見出しの階層構造を取得."""
    t = transparse(_s)
    st = SourceTree.create(t, "source1")

    assert st.root == Heading(title="source1", level=1)
    h2 = Heading(title="2.1", level=2)
    assert st.children(st.root) == [h2]
    h3 = Heading(title="3.1", level=3)
    h31 = Heading(title="3. dedent", level=3)
    h32 = Heading(title="3. same level", level=3)
    h33 = Heading(title="3. same level", level=3)
    assert st.children(h2) == [h3, h31, h32, h33]
    h4 = Heading(title="4.1", level=4)
    assert st.children(h3) == [h4]
    h5 = Heading(title="5.1", level=5)
    assert st.children(h4) == [h5]
    h6 = Heading(title="6.1", level=6)
    assert st.children(h5) == [h6]
    assert st.children(h6) == []
