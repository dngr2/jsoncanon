import pytest
from jsoncanon.types import FinalJson


@pytest.mark.parametrize(
    'raw_json_str',
    [
        'test',
        '45.67',
    ],
)
def test_raw_json(raw_json_str: str) -> None:
    final_json = FinalJson(raw_json_str)
    assert not isinstance(final_json, str)
    assert final_json != raw_json_str
    assert str(final_json) == raw_json_str
    assert repr(final_json) == f"FinalJson('{raw_json_str}')"
