"""用語関連."""



from knowde.complex.__core__.tree2net import parse2net


def test_duplicable() -> None:
    """重複可能な文."""
    _s = r"""
        # h1
            1
                +++ dup1 +++
                +++ dup1 +++
                +++ dup1 +++
            2
    """
    _sn = parse2net(_s)


def test_add_resolved_edge() -> None:
    """parse2net版."""
    _s = r"""
        # h1
            A: df
            B: b{A}b
            C{B}: ccc
            D: d{CB}d
        ## h2
            P{D}: ppp
            Q: qqq
            X:
    """
    sn = parse2net(_s)
    assert sn.get_resolved("df") == {}
    assert sn.get_resolved("b{A}b") == {"df": {}}
    assert sn.get_resolved("ccc") == {"b{A}b": {"df": {}}}
    assert sn.get_resolved("d{CB}d") == {"ccc": {"b{A}b": {"df": {}}}}
    assert sn.get_resolved("ppp") == {"d{CB}d": {"ccc": {"b{A}b": {"df": {}}}}}
    assert sn.get_resolved("qqq") == {}


# def test_duplicate_term() -> None:
#     """用語の重複は弾く."""
#     _s = r"""
#         # names
#             name1:
#             name1:
#     """
#     with pytest.raises(TermConflictError):
#         parse2net(_s)


# def test_parse_terms() -> None:
#     """用語一覧."""
#     _s = r"""
#         # h1
#           n1,n11:
#           P1 |line,l1:
#           P2 |def,d1: de\
#                 f
#         ## h2
#           n2,n21:
#           P3 |line2,l2,l21:
#           P4 |def2,d2: def
#           P5 |aaa
#     """
#     t = transparse(_s)
#     s = get_termspace(t)
#     assert s.origins == unordered(
#         [
#             Term.create("n1", "n11"),
#             Term.create("line", "l1", alias="P1"),
#             Term.create("def", "d1", alias="P2"),
#             Term.create("n2", "n21"),
#             Term.create("line2", "l2", "l21", alias="P3"),
#             Term.create("def2", "d2", alias="P4"),
#             Term.create(alias="P5"),
#         ],
#     )


# # def test_formula() -> None:
# #     """数式に含まれる=は無視して文字列として扱いたい."""
# #     _s = r"""
# #         # h1
# #           量化子の順序によって意味が変わる
# #             n1: $\forall{x}\exists{y}R(x, y=t)$
# #             n2,n22: xx$R(x, y=t)$xx
# #         ## h2
# #           P1 |xx$y=t$xx
# #           P2 |xx$y=t$xx \
# #                   yyyy
# #             <-> J13 |サールの反証: {平叙文}から{評価文}を結論する論証
# #             e.g. P41|「XXXならば明日ヒョウが降るよw」
# #     """
# #     t = transparse(_s)
# #     x = get_termspace(t)
# #     assert len(x) == 3
# #     assert x.aliases == unordered(["P1", "P2", "J13", "P41"])


# def test_parse_context() -> None:
#     """名前一覧."""
#     _s = r"""
#         # context
#             ctx1
#                 -> b1
#                     -> bb1
#                     -> bb2
#                 -> b2
#                 <- c
#                 <-> d
#                 e.g. example
#                 g.e. general
#                 ref. ref
#                 1. one
#                 2. two
#     """
#     _t = transparse(_s)
#     st = tree2statements(_t).contexted("ctx1")
#     assert st.thus == unordered(["b1", "b2"])
#     assert st.cause == unordered(["c"])
#     assert st.example == unordered(["example"])
#     assert st.general == unordered(["general"])
#     assert st.ref == unordered(["ref"])
#     assert st.list == ["one", "two"]
