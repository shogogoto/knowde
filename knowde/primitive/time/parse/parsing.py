"""pyparsing関連."""

from functools import cache

from pyparsing import (
    Literal,
    Optional,
    ParserElement,
    Word,
    alphas,
    nums,
    oneOf,
)


@cache
def p_interval() -> ParserElement:
    """EDTFのintervalを判別."""
    slash = Literal("/")
    dots = Literal("..")
    hyphen = Literal("-")

    year = Optional(hyphen) + Word(nums, exact=4)
    month = Word(nums, min=1, max=2)
    day = Word(nums, min=1, max=2)
    date = year + Optional(hyphen + month + Optional(hyphen + day))
    return (
        (date + slash + date)  # 1964/2008
        | (date + slash + dots)  # open end ex. 1985/..
        | (dots + slash + date)  # open start ex.  ../1985
    )


@cache
def p_jp() -> ParserElement:
    """和暦パターン."""
    # era_head = oneOf(["M", "T", "S", "H", "R"])
    era_head = Word(alphas.upper(), exact=1)
    xx = Word(nums, min=1, max=2)
    y = era_head + xx
    sep = oneOf(["/", "-"])
    m = sep + xx
    d = sep + xx
    return y + Optional(m + Optional(d))
