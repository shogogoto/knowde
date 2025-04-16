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
from knowde.primitive.__core__.neoutil import UUIDy, to_uuid
from knowde.primitive.term import Term
from knowde.primitive.user.repo import LUser

from . import KAdjacency, Knowde


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
) -> tuple[SysNet, MResource]:
    """テキストを保存."""
    meta = txt2meta(s)
    meta.path = path
    ns = fetch_namespace(to_uuid(user_id))
    save_resource(meta, ns)
    r = ns.get_resource(meta.title)
    sn = parse2net(s)
    sn2db(sn, r.uid)
    return sn, r


def search_knowde(
    s: str,
) -> list:
    """用語、文のいずれかでマッチするものを返す."""
    q = r"""
        CALL {
            // 検索文字列が含まれる文 bA123
            MATCH (sent1: Sentence WHERE sent1.val CONTAINS $s)
            OPTIONAL MATCH (term1: Term)-[:DEF|ALIAS]->(sent1)
            OPTIONAL MATCH (term1)-[:ALIAS]-*(name1: Term)
            RETURN sent1 as sent,  COLLECT(name1) as names
            UNION
            // 検索文字列が含まれる用語
            MATCH (term2: Term WHERE term2.val CONTAINS $s),
            (n1)-[:ALIAS]-*(term2: Term)-[:ALIAS]-*(n2: Term)
                -[:DEF]->(sent3: Sentence)
            UNWIND [n2, n1] as name3
            RETURN sent3 as sent, COLLECT(DISTINCT name3) as names
        }
        WITH sent, names // 中間結果のサイズダウン
        OPTIONAL MATCH (sent)<-[:TO]-{1,}(premise:Sentence)
        OPTIONAL MATCH (sent)-[:TO]->{1,}(conclusion:Sentence)
        OPTIONAL MATCH p_leaf = (sent)-[:TO]->{1,}(leaf:Sentence)
            WHERE NOT (leaf)-[:TO]->(:Sentence)
        OPTIONAL MATCH p_axiom = (axiom:Sentence)-[:TO]->{1,}(sent)
            WHERE NOT (:Sentence)-[:TO]->(axiom)
        OPTIONAL MATCH (sent)<-[:RESOLVED]-{1,}(referred:Sentence)
        OPTIONAL MATCH (sent)-[:RESOLVED]->{1,}(refer:Sentence)
        OPTIONAL MATCH (sent)-[:BELOW]->(:Sentence)
            -[:SIBLING|BELOW]->*(detail:Sentence)

        WITH sent, names
        , COUNT(DISTINCT premise) AS n_premise
        , COUNT(DISTINCT conclusion) AS n_conclusion
        , MAX(coalesce(length(p_axiom), 0)) AS dist_axiom
        , MAX(coalesce(length(p_leaf), 0)) AS dist_leaf
        , COUNT(DISTINCT referred) AS n_referred
        , COUNT(DISTINCT refer) AS n_refer
        , COUNT(DISTINCT detail.val) AS n_detail

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
        OPTIONAL MATCH (detail)<-[:DEF]-(t_detail: Term)
        RETURN sent, names, intv
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
            , {
                n_premise: n_premise,
                n_conclusion: n_conclusion,
                dist_axiom: dist_axiom,
                dist_leaf: dist_leaf,
                n_referred: n_referred,
                n_refer: n_refer,
                n_detail: n_detail
                } AS stats
    """
    res = db.cypher_query(
        q,
        params={"s": s},
        resolve_objects=True,
    )

    def neocol2knowde(col: list) -> list[Knowde]:
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
    for (
        sent,
        names,
        intv,
        premises,
        conclusions,
        refers,
        referreds,
        details,
        _stats,
    ) in res[0]:
        adj = KAdjacency(
            center=Knowde(
                sentence=str(sent.val),
                term=Term.from_labels(collapse(names)),
                uid=sent.uid,
            ),
            when=intv.val if intv else None,
            details=neocol2knowde(details),
            premises=neocol2knowde(premises),
            conclusions=neocol2knowde(conclusions),
            refers=neocol2knowde(refers),
            referreds=neocol2knowde(referreds),
        )
        ls.append(adj)
    return ls


def get_stats_by_id(uid: UUIDy) -> list[int] | None:
    """systats相当のものをDBから取得する(用)."""
    q = r"""
        MATCH (tgt:Sentence) WHERE tgt.uid= $uid
        // 自身を含めないように 1以上
        // TO
        OPTIONAL MATCH (tgt)<-[:TO]-{1,}(premise:Sentence)
        OPTIONAL MATCH (tgt)-[:TO]->{1,}(conclusion:Sentence)
        OPTIONAL MATCH p_leaf = (tgt)-[:TO]->{1,}(leaf:Sentence)
            WHERE NOT (leaf)-[:TO]->(:Sentence)
        OPTIONAL MATCH p_axiom = (axiom:Sentence)-[:TO]->{1,}(tgt)
            WHERE NOT (:Sentence)-[:TO]->(axiom)
        OPTIONAL MATCH (tgt)<-[:RESOLVED]-{1,}(referred:Sentence)
        OPTIONAL MATCH (tgt)-[:RESOLVED]->{1,}(refer:Sentence)
        OPTIONAL MATCH (tgt)-[:BELOW]->(:Sentence)
            -[:SIBLING|BELOW]->*(detail:Sentence)

        RETURN
          COUNT(DISTINCT premise) AS n_premise
        , COUNT(DISTINCT conclusion) AS n_conclusion
        , MAX(coalesce(length(p_axiom), 0)) AS dist_axiom
        , MAX(coalesce(length(p_leaf), 0)) AS dist_leaf
        , COUNT(DISTINCT referred) AS n_referred
        , COUNT(DISTINCT refer) AS n_refer
        , COUNT(DISTINCT detail.val) AS n_detail

    """
    res = db.cypher_query(
        q,
        params={"uid": to_uuid(uid).hex},
        resolve_objects=True,
    )
    return res[0][0] if res else None
