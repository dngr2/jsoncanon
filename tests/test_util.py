from types import NoneType

from jsoncanon.util import ensure_plain_type


def test_ensure_plain_type() -> None:
    assert ensure_plain_type(NoneType) is NoneType
    assert ensure_plain_type(int) is int
    assert ensure_plain_type(list) == list
    assert ensure_plain_type(list[str]) == list
    assert ensure_plain_type(dict[int, int]) == dict
