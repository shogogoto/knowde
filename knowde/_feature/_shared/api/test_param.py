from .param import ApiParam


class OnePatam(ApiParam, frozen=True):
    p1: str
    p2: int


# def test_makefunc() -> None:
#     op = OnePatam(p1="s", p2=0)
#     print(op.makefunc())
