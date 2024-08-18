"""for unit test."""
from knowde.complex.definition.repo.definition import add_definition
from knowde.complex.definition.repo.statistics import find_statistics


def test_isolate_stats() -> None:
    """孤立した定義."""
    d = add_definition("p1", "s1")
    stat = find_statistics(d.valid_uid)
    assert stat.nums == (0, 0, 0, 0)


def test_1src() -> None:
    """依存元srcが1つ."""
    # p1 <- p2
    d1 = add_definition("p1", "s1")
    d2 = add_definition("p2", "s2-{p1}")
    stat1 = find_statistics(d1.valid_uid)
    assert stat1.nums == (0, 1, 0, 1)
    stat2 = find_statistics(d2.valid_uid)
    assert stat2.nums == (1, 0, 1, 0)


def test_2sibling_src() -> None:
    """兄弟."""
    # p1, p2 <- p3
    d1 = add_definition("p1", "s1")
    d2 = add_definition("p2", "s2")
    d3 = add_definition("p3", "s3{p1}{p2}")

    stat1 = find_statistics(d1.valid_uid)
    assert stat1.nums == (0, 1, 0, 1)
    stat2 = find_statistics(d2.valid_uid)
    assert stat2.nums == (0, 1, 0, 1)
    stat3 = find_statistics(d3.valid_uid)
    assert stat3.nums == (2, 0, 1, 0)


def test_3layers() -> None:
    """三層."""
    # p11, p12 <- p21
    # p13 <- p22
    # p21, p22 <- p31
    d11 = add_definition("p11", "s11")
    d12 = add_definition("p12", "s12")
    d13 = add_definition("p13", "s13")
    d21 = add_definition("p21", "{p11}{p12}")
    d22 = add_definition("p22", "{p13}")
    d31 = add_definition("p31", "{p21}{p22}")

    stat11 = find_statistics(d11.valid_uid)
    stat12 = find_statistics(d12.valid_uid)
    stat13 = find_statistics(d13.valid_uid)
    stat21 = find_statistics(d21.valid_uid)
    stat22 = find_statistics(d22.valid_uid)
    stat31 = find_statistics(d31.valid_uid)

    assert stat11.nums == (0, 2, 0, 2)
    assert stat12.nums == (0, 2, 0, 2)
    assert stat13.nums == (0, 2, 0, 2)
    assert stat21.nums == (2, 1, 1, 1)
    assert stat22.nums == (1, 1, 1, 1)
    assert stat31.nums == (5, 0, 2, 0)
