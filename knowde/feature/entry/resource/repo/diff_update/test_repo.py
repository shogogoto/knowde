"""更新差分repo test."""

from time import sleep

import networkx as nx
from pytest_unordered import unordered

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.repo.diff_update.domain import (
    identify_duplicate_updiff,
)
from knowde.feature.entry.resource.repo.diff_update.repo import update_resource_diff
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.nxutil import nxprint
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="one@gmail.com").save()


async def common(  # noqa: D103
    u: LUser,
    old: str,
    upd: str,
    do_print: bool = False,  # noqa: FBT001, FBT002
    do_sleep: bool = False,  # noqa: FBT001, FBT002
) -> None:
    _, rm = await save_text(u.uid, old)
    sn = parse2net(upd)
    await update_resource_diff(rm.uid, sn, do_print)
    db_sn, _ = await restore_sysnet(rm.uid)
    dupmap = identify_duplicate_updiff(sn, db_sn)
    if do_print:
        print("--------- TXT")  # noqa: T201
        nxprint(sn.g, True)  # noqa: FBT003
        print("--------- DB")  # noqa: T201
        nxprint(db_sn.g, True)  # noqa: FBT003
        # print("--------- TXT - DB edges")
        # pp(set(sn.g.edges()) - set(db_sn.g.edges()))
        print(f"{dupmap=}")  # noqa: T201
    if do_sleep:
        sleep(1000)  # noqa: ASYNC251

    # 元のuidを尊重するため、updのsnのduplicable uidは変更される
    # なのでそれを補正して比較
    g = nx.relabel_nodes(sn.g, dupmap) if len(dupmap) > 0 else sn.g

    assert g.edges() == unordered(db_sn.g.edges())


@mark_async_test()
async def test_update_add_sent(u: LUser) -> None:
    """単文追加."""
    old = """
        # title1
            aaa
            bbb
    """
    upd = """
        # title1
            aaa
                aaa1
            bbb
            ccc
    """
    await common(u, old, upd)


@mark_async_test()
async def test_update_edge(u: LUser) -> None:
    """関係のみ更新."""
    old = """
        # title1
            aaa
                bbb
            ccc
    """
    upd = """
        # title1
            aaa
            bbb
                -> ccc
    """
    await common(u, old, upd)


@mark_async_test()
async def test_update_terms(u: LUser) -> None:
    """用語更新."""
    # aaa 用語追加
    # bbb 用語削除
    # ccc 用語変更
    # ddd 3名の用語を削除
    # eee 名の削除と追加
    old = """
        # title1
            zero: 000
            aaa
            B: bbb
            C: ccc
            D,D1,D2: ddd
            E,E1: eee
    """
    upd = """
        # title1
            zero: 000
            A: aaa
            bbb
            CC: ccc
            ddd
            E1,E2,E3: eee
    """
    await common(u, old, upd)


@mark_async_test()
async def test_update_defs(u: LUser) -> None:
    """用語と単文を同時に変更."""
    old = """
        # title1
            A: aaa
            B: bbb
    """
    upd = """
        # title1
            A,A1,A2: aad
            B: bbbbb
    """
    await common(u, old, upd)


@mark_async_test()
async def test_switch_term(u: LUser) -> None:
    """単文そのままに用語だけを入れ替える."""
    old = """
        # title1
            A: aaa
            B: bbb
    """
    upd = """
        # title1
            B: aaa
            A: bbb
    """
    await common(u, old, upd)


@mark_async_test()
async def test_update_nosentence_def(u: LUser) -> None:
    """無単文定義対応."""
    old = """
        # title1
            A:
            B: bbb
            C: ccc
    """
    upd = """
        # title1
            A: aaa
            B:
            C: ccc
            D:
    """
    await common(u, old, upd)


@mark_async_test()
async def test_update_duplicable(u: LUser) -> None:
    """重複可能文."""
    old = """
        # title1
            +++ aaa +++
            +++ xxx +++
    """
    upd = """
        # title1
            +++ bbb +++
            +++ xxx +++
            +++ xxx +++
            +++yyy+++
            +++yyy+++
    """
    await common(u, old, upd)


# @mark_async_test()
# async def test_update_when(u: LUser) -> None:
#     """無単文定義対応."""
#     old = """
#         # title1
#             A:
#             B: bbb
#             C: ccc
#     """
#     upd = """
#         # title1
#             A: aaa
#             B:
#             C: ccc
#             D:
#     """
#     await common(u, old, upd)
