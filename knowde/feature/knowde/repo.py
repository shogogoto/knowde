"""repo."""

from collections.abc import Generator
from contextlib import contextmanager

from more_itertools import collapse
from neomodel import db
from pydantic import BaseModel, PrivateAttr

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.entry import NameSpace
from knowde.complex.entry.category.folder.repo import fetch_namespace
from knowde.complex.entry.label import LFolder
from knowde.complex.entry.mapper import MResource
from knowde.complex.entry.namespace import fill_parents, save_resource
from knowde.complex.entry.namespace.sync import txt2meta
from knowde.complex.nxdb.save import sn2db
from knowde.feature.knowde.cypher import (
    OrderBy,
    Paging,
    WherePhrase,
    q_sentence_from_def,
    q_stats,
)
from knowde.primitive.__core__.neoutil import UUIDy, to_uuid
from knowde.primitive.term import Term
from knowde.primitive.user.repo import LUser

from . import KAdjacency, Knowde, KStats


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
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[SysNet, MResource]:
    """テキストを保存."""
    meta = txt2meta(s)
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
        CALL {
        """
        + q_sentence_from_def(wp)
        + """
        }
        WITH sent, names // 中間結果のサイズダウン
        CALL {
            WITH sent, names
        """
        + q_stats("sent")
        + """
        }
        WITH sent, names
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

        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        OPTIONAL MATCH (sent)<-[:TO]-(premise:Sentence)
        OPTIONAL MATCH (premise)<-[:DEF]-(t_pre: Term)
        OPTIONAL MATCH (sent)-[:TO]->(conclusion:Sentence)
        OPTIONAL MATCH (conclusion)<-[:DEF]-(t_con: Term)
        OPTIONAL MATCH (sent)<-[:RESOLVED]-(referred:Sentence)
        OPTIONAL MATCH (referred)<-[:DEF]-(t_refd: Term)
        OPTIONAL MATCH (sent)-[:RESOLVED]->(refer:Sentence)
        OPTIONAL MATCH (refer)<-[:DEF]-(t_ref: Term)
        OPTIONAL MATCH (sent)-[:BELOW]->(detail:Sentence)
        OPTIONAL MATCH (detail)-[:SEBLING]->*(detail2)
        OPTIONAL MATCH (detail)<-[:DEF]-(t_detail: Term)
        WITH sent, names, intv
            , COLLECT(DISTINCT CASE WHEN premise IS NOT NULL
                THEN [premise.val, premise.uid, t_pre.val] END) AS premises
            , COLLECT(DISTINCT CASE WHEN conclusion IS NOT NULL
                THEN [conclusion.val, conclusion.uid, t_con.val] END) AS conclusions
            , COLLECT(DISTINCT CASE WHEN refer IS NOT NULL
                THEN [refer.val, refer.uid, t_ref.val] END) AS refers
            , COLLECT(DISTINCT CASE WHEN referred IS NOT NULL
                THEN [referred.val, referred.uid, t_refd.val] END) AS referreds
            , COLLECT(DISTINCT CASE WHEN detail IS NOT NULL
                THEN [detail.val, detail.uid, t_detail.val] END) AS details
            , stats
            """
        + (order_by.phrase() if order_by else "")
        + paging.phrase()
        + """
        RETURN sent
            , names
            , intv
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

    def _neocol2knowde(col: list) -> list[Knowde]:
        """neomodelのcollected listを変換."""
        return [
            Knowde(
                sentence=str(sent),
                uid=uid,
                term=Term.create(name) if name else None,
            )
            for sent, uid, name in collapse(col, levels=2)
        ]

    ls = []
    for row in res[0]:
        (
            sent,
            names,
            intv,
            premises,
            conclusions,
            refers,
            referreds,
            details,
            stats,
        ) = row
        adj = KAdjacency(
            center=Knowde(
                sentence=str(sent.val),
                term=Term.from_labels(collapse(names)),
                uid=sent.uid,
            ),
            when=intv.val if intv else None,
            details=_neocol2knowde(details),
            premises=_neocol2knowde(premises),
            conclusions=_neocol2knowde(conclusions),
            refers=_neocol2knowde(refers),
            referreds=_neocol2knowde(referreds),
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
