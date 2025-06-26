"""repo."""

from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from more_itertools import collapse
from neomodel import db
from pydantic import BaseModel, PrivateAttr

from knowde.feature.auth.repo.repo import LUser
from knowde.feature.entry import NameSpace
from knowde.feature.entry.category.folder.repo import fetch_namespace
from knowde.feature.entry.label import LFolder
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.namespace import fill_parents, save_resource
from knowde.feature.entry.namespace.sync import txt2meta
from knowde.feature.knowde.cypher import (
    OrderBy,
    Paging,
    WherePhrase,
    q_sentence_from_def,
    q_stats,
)
from knowde.feature.knowde.detail import fetch_knowde_by_ids
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.feature.stats.nxdb.save import sn2db
from knowde.shared.types import UUIDy, to_uuid

from . import KAdjacency, KStats


# fsと独
class NameSpaceRepo(BaseModel, arbitrary_types_allowed=True):
    """user namespace."""

    user: LUser
    _ns: NameSpace | None = PrivateAttr(default=None)

    @contextmanager
    def ns_scope(self) -> Generator[NameSpace]:
        """何度もfetchしたくない."""  # noqa: DOC402
        ns = fetch_namespace(self.user.uid)
        try:
            self._ns = ns
            yield ns
        finally:
            self._ns = None

    def add_folders(self, *names: str) -> LFolder:
        """Return tail folder."""
        if self._ns is not None:
            return fill_parents(self._ns, *names)
        with self.ns_scope() as ns:
            return fill_parents(ns, *names)


def save_text(
    user_id: UUIDy,
    s: str,
    path: tuple[str, ...] | None = None,
    updated: datetime | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[SysNet, MResource]:
    """テキストを保存."""
    meta = txt2meta(s)
    meta.updated = updated
    meta.path = path
    ns = fetch_namespace(to_uuid(user_id))
    save_resource(meta, ns)
    r = ns.get_resource(meta.title)
    sn = parse2net(s)
    sn2db(sn, r.uid, do_print=do_print)
    return sn, r


def search_total(
    s: str,
    wp: WherePhrase = WherePhrase.CONTAINS,
) -> int:
    """検索文字列にマッチするknowde総数."""
    q_tot = (
        """
        CALL {
        """
        + q_sentence_from_def(wp)
        + """
        }
        RETURN COUNT(sent)
    """
    )
    res = db.cypher_query(
        q_tot,
        params={"s": s},
    )
    return res[0][0][0]


def search_knowde(
    s: str,
    wp: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy = OrderBy(),
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[int, list[KAdjacency]]:
    """用語、文のいずれかでマッチするものを返す."""
    q = (
        r"""
        CALL () {
        """
        + q_sentence_from_def(wp)
        + """
        }
        WITH sent // 中間結果のサイズダウン
        CALL (sent){
        """
        + q_stats("sent")
        + """
        }
        WITH sent
            , {
                n_premise: n_premise,
                n_conclusion: n_conclusion,
                dist_axiom: dist_axiom,
                dist_leaf: dist_leaf,
                n_referred: n_referred,
                n_refer: n_refer,
                n_detail: n_detail
                """
        + (order_by.score_prop() if order_by else "")
        + """
            } AS stats
        OPTIONAL MATCH (sent)<-[:TO]-(premise:Sentence)
        OPTIONAL MATCH (sent)-[:TO]->(conclusion:Sentence)
        OPTIONAL MATCH (sent)<-[:RESOLVED]-(referred:Sentence)
        OPTIONAL MATCH (sent)-[:RESOLVED]->(refer:Sentence)
        OPTIONAL MATCH (sent)-[:BELOW]->(detail1:Sentence)
        // 近接1階層分だか SIB or BELOW で全てを辿るのではない
        OPTIONAL MATCH (detail1)-[:SIBLING]->*(detail2:Sentence)
        UNWIND [detail1, detail2] as detail
        WITH sent
            , COLLECT(DISTINCT premise.uid) as premises
            , COLLECT(DISTINCT conclusion.uid) as conclusions
            , COLLECT(DISTINCT referred.uid) as referreds
            , COLLECT(DISTINCT refer.uid) as refers
            , COLLECT(DISTINCT detail.uid) as details
            , stats
            """
        + (order_by.phrase() if order_by else "")
        + paging.phrase()
        + """
        RETURN sent.uid as sent_uid
            , premises, conclusions
            , refers, referreds
            , details
            , stats
        """
    )
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(
        q,
        params={"s": s},
        resolve_objects=True,
    )

    def is_valid_uuid(uuid_string) -> bool:
        try:
            UUID(uuid_string)
            return True  # noqa: TRY300
        except ValueError:
            return False

    uids = set(filter(is_valid_uuid, collapse(res, base_type=UUID)))
    knowdes = fetch_knowde_by_ids(list(uids))
    ls = []
    for row in res[0]:
        (
            sent,
            premises,
            conclusions,
            refers,
            referreds,
            details,
            stats,
        ) = row
        adj = KAdjacency(
            center=knowdes[sent],
            details=[knowdes[d] for d in details[0]],
            premises=[knowdes[p] for p in premises[0]],
            conclusions=[knowdes[c] for c in conclusions[0]],
            refers=[knowdes[r] for r in refers[0]],
            referreds=[knowdes[r] for r in referreds[0]],
            stats=KStats.model_validate(stats),
        )
        ls.append(adj)
    total = search_total(s, wp)
    return total, ls


def get_stats_by_id(uid: UUIDy) -> list[int] | None:
    """systats相当のものをDBから取得する(用)."""
    q = rf"""
        MATCH (tgt:Sentence) WHERE tgt.uid= $uid
        {q_stats("tgt")}
    """
    res = db.cypher_query(
        q,
        params={"uid": to_uuid(uid).hex},
        resolve_objects=True,
    )
    return res[0][0] if res else None
