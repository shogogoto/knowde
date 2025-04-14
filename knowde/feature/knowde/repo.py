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


def save_text(user_id: UUIDy, s: str, path: tuple[str, ...] | None = None) -> SysNet:
    """テキストを保存."""
    meta = txt2meta(s)
    meta.path = path
    ns = fetch_namespace(to_uuid(user_id))
    save_resource(meta, ns)
    r = ns.get_resource(meta.title)
    sn = parse2net(s)
    sn2db(sn, r.uid)
    return sn


def search_knowde(s: str) -> list:
    """用語、文のいずれかでマッチするものを返す."""
    q = """
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
                THEN [premise.val, premise.uid, t_pre.val] END) as premises
            , COLLECT(DISTINCT CASE WHEN conclusion IS NOT NULL
                THEN [conclusion.val, conclusion.uid, t_con.val] END) as conclusions
            , COLLECT(DISTINCT CASE WHEN refer IS NOT NULL
                THEN [refer.val, refer.uid, t_ref.val] END) as refers
            , COLLECT(DISTINCT CASE WHEN referred IS NOT NULL
                THEN [referred.val, referred.uid, t_refd.val] END) as referreds
            , COLLECT(DISTINCT CASE WHEN detail IS NOT NULL
                THEN [detail.val, detail.uid, t_detail.val] END) as details

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
