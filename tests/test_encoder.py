import pytest
from jsoncanon.encoder import FinalJsonEncoder
from jsoncanon.types import FinalJson, JsonWithFinal


@pytest.mark.parametrize(
    'data, expected',
    [
        ('test', '"test"'),
        (123, '123'),
        (123.456, '123.456'),
        (True, 'true'),
        (False, 'false'),
        (None, 'null'),
        ([123, '456'], '[123, "456"]'),
        ({'key': 'value'}, '{"key": "value"}'),
        (FinalJson('test'), 'test'),
    ],
    ids=['str', 'int', 'float', 'true', 'false', 'null', 'list', 'dict', 'FinalJson'],
)
def test_final_json_encoder(data: JsonWithFinal, expected: str) -> None:
    encoder = FinalJsonEncoder(ensure_ascii=False)
    encoded = encoder.encode(data)
    assert encoded == expected


def test_raw_json_encoder_ensure_ascii_true() -> None:
    with pytest.raises(AssertionError, match='FinalJsonEncoder requires ensure_ascii=False'):
        FinalJsonEncoder(ensure_ascii=True)
