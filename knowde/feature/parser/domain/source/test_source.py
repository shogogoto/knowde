"""test source parsing."""
from datetime import date

import pytest

from knowde.feature.parser.domain.errors import SourceMatchError
from knowde.feature.parser.domain.parser.parser import transparse
from knowde.feature.parser.domain.source import get_source


def test_parse_heading() -> None:
    """情報源について."""
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
    t = transparse(_s)
    s1 = get_source(t, "source1")
    assert s1.about.tuple == ("source1", "tanaka tarou", date(2020, 11, 11))
    s2 = get_source(t, "source2")
    assert s2.about.tuple == ("source2", None, None)
    with pytest.raises(SourceMatchError):
        get_source(t, "source")
    with pytest.raises(SourceMatchError):
        get_source(t, "xxx")
