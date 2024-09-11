"""textから章節を抜き出す.

知りたいこと
sourceごと
名前一覧
名前衝突チェック
言明一覧
言明の依存関係情報
文字列への復元
"""

from datetime import date

import pytest
from lark import Tree

from knowde.feature.parser.domain.knowde import RootTree
from knowde.feature.parser.domain.parser import transparse
from knowde.feature.parser.domain.source import SourceMatchError
from knowde.feature.parser.domain.transformer import common_transformer


def _echo(t: Tree) -> None:
    print(t)  # noqa: T201
    print(t.pretty())  # noqa: T201


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
    t = transparse(_s, common_transformer())
    rt = RootTree(tree=t)
    s1 = rt.get_source("source1")
    assert s1.info.tuple == ("source1", "tanaka tarou", date(2020, 11, 11))
    s2 = rt.get_source("source2")
    assert s2.info.tuple == ("source2", None, None)

    with pytest.raises(SourceMatchError):
        rt.get_source("source")

    with pytest.raises(SourceMatchError):
        rt.get_source("xxx")


def test_parse_multiline() -> None:
    """改行ありで一行とみなす."""
    _s = r"""
        # src
            ! multiline
            aaa_\
            bbb
                ccc
                ddd
                mul1 \
                    mul2 \
                        mul3
    """
    t = transparse(_s, common_transformer())
    _rt = RootTree(tree=t)


def test_parse_define_and_names() -> None:
    """定義を読み取る."""
    _s = r"""
        # names
            ! define

            name1: def1
            name2=name3: def2
            name22 = name3: def2
            name4 = name5 = name6: def3
            name7: deffffffffffffffffffffffffffffffffffffffffffffff
            alias |namenamename: defdefdefdef
            ! var
            xxx
                xxx{name1}xxx
    """
    t = transparse(_s, common_transformer())
    _rt = RootTree(tree=t)
    # t = transparse(_s, common_transformer())


def test_parse_context() -> None:
    """名前一覧."""
    _s = r"""
        # context
            ! context
            ctx1
            -> b1
            -> b2
            <- c
            <-> d
            e.g. example
            g.e. general
            ref. ref
    """
    t = transparse(_s, common_transformer())
    _rt = RootTree(tree=t)


def test_parse_real_text() -> None:
    """実際のメモ."""
    _s = """
    # アジャイルサムライ
      @author ジョナサン・ラスマセン
    ## 1. 「アジャイル」入門
    ### 1. ざっくりわかるアジャイル開発
      金を支払う顧客にとって信頼できる
        一番大事だと思うテスト済みの機能を毎週必ず届けてくれる
        <-> 大量の実行計画、製品文章、作業報告書を納品してくれる

      開発チームが大事にしなければならないこと
      1. 大きな問題は小さくする: 短い１週間で成果を出せる単位に分割
        プロジェクト規模によっては２-３週単意
        大抵はプロジェクト初期は２週単位
      2. 本当に大事なことに集中して、それ以外のことは忘れる
        実施計画書などのドキュメントは必要だが、動くソフトウェアの補完でしかない

    !  3. ちゃんと動くソフトウェアを届ける:
    !    もっと早くこまめにたくさんテストする。テストを疎かにしない。
    !  4. フィードバックを求める:
    !    定期的な顧客に答えの確認なしに道に迷わないなんてできない
    !    顧客はこれなしにプロジェクトのハンドルなんて切れない
    !    顧客に判断材料を与えないと開発者は身動き取れなくなる
    !  5. 必要とあらば進路を変える:
    !    今週大事なことでも来週にはどうでもよくなるかも
    !    計画に従っているだけでは対処できない
    !    計画を変えよ、現実ではなく。

    """
