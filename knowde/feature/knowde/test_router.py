"""knowde router test."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
import pytz
from fastapi import status
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.feature.auth.repo.repo import LUser
from knowde.feature.knowde import KnowdeDetail
from knowde.feature.knowde.repo import save_text
from knowde.feature.stats.nxdb import LSentence, LTerm


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="onex@gmail.com", hashed_password="xxx").save()  # noqa: S106


def test_detail_router(u: LUser, caplog):
    """Router testは1つはしておくけど細かいケースはrepositoryなどでやっておく."""
    client = TestClient(root_router())
    res = client.get("/knowde/sentence/064ef00c-5e33-4505-acf5-45ba26cc54dc")
    assert res.status_code == status.HTTP_404_NOT_FOUND

    s = """
    # titleX
    ## head1
    ### head2
        parent
            when. 19C
            p1
            p2
                p21
            p3
    """
    t = datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    _sn, _r = save_text(
        u.uid,
        s,
        # DB readしたときにneo4j.DateTimeが返ってきて
        # pydanticとvalidate error にならないかチェック
        updated=t,
        path=("A", "B", "C.txt"),
    )

    s = LSentence.nodes.get(val="p21")
    url = f"/knowde/sentence/{UUID(s.uid)}"
    res = client.get(url)
    assert res.status_code == status.HTTP_200_OK
    d = KnowdeDetail.model_validate(res.json())

    assert d.location.resource.updated == t
    assert d.location.user.uid.hex == u.uid
    assert [f.val for f in d.location.folders] == ["A", "B"]


@pytest.mark.skip
def test_search(u: LUser, caplog):
    """本番でのapi callを模擬(重いからskip."""
    client = TestClient(root_router())

    p = Path(__file__).parent / "fixture" / "test.txt"
    s = p.read_text()
    _sn, _r = save_text(u.uid, s)
    s = LTerm.nodes.get(val="アルキメデス").sentence.single()
    url = "/knowde/?q=%E6%95%B0%E5%AD%A6&type=CONTAINS&page=1&size=100&n_detail=1&n_premise=3&n_conclusion=3&n_refer=3&n_referred=3&dist_axiom=1&dist_leaf=1&desc=true"  # noqa: E501
    res = client.get(url)
    assert res.status_code == status.HTTP_200_OK
