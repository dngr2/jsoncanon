from enum import IntEnum
from types import NoneType
from typing import Annotated

from jsoncanon.util import ensure_plain_type, JSON, JSON_Dict, JSON_List, JsonDataPreprocessor
import pytest


def test_ensure_plain_type() -> None:
    assert ensure_plain_type(NoneType) is NoneType
    assert ensure_plain_type(int) is int
    assert ensure_plain_type(list) == list
    assert ensure_plain_type(list[str]) == list
    assert ensure_plain_type(dict[int, int]) == dict


def invalid_preproc_func_two_params(i: int, s: str) -> str:
    ...


def invalid_preproc_func_one_param_pos_or_keyword(s: str) -> str:
    ...


def invalid_preproc_func_one_param_no_annotation(s) -> str:
    ...


def invalid_preproc_func_no_return_annotation(s) -> str:
    ...


@pytest.mark.parametrize(
    "preproc_func",
    [
        invalid_preproc_func_two_params,
        invalid_preproc_func_one_param_pos_or_keyword,
        invalid_preproc_func_one_param_no_annotation,
        invalid_preproc_func_no_return_annotation,
    ],
)
def test_json_preprocessor_valid_funcs(preproc_func) -> None:
    with pytest.raises(AssertionError):
        JsonDataPreprocessor([preproc_func])


@pytest.fixture
def json_data_preprocessor() -> JsonDataPreprocessor:
    def str_upper_func(s: str, /) -> str:
        return s.upper()

    def int_increase_func(i: int, /) -> int:
        return i + 1

    def float_halve_func(f: float, /) -> float:
        return f / 2

    def float_to_str_func(f: float, /) -> str:
        return str(f)

    def bool_invert_func(b: bool, /) -> bool:
        return not b

    def none_to_str_func(n: NoneType, /) -> str:
        return str(n)

    def dict_upper_keys_func(d: JSON_Dict, /) -> JSON_Dict:
        return {key.upper(): val for key, val in d.items()}

    def list_reverse_func(li: JSON_List, /) -> JSON_List:
        return [_ for _ in reversed(li)]

    return JsonDataPreprocessor([
        str_upper_func,
        int_increase_func,
        float_halve_func,
        float_to_str_func,
        bool_invert_func,
        none_to_str_func,
        dict_upper_keys_func,
        list_reverse_func,
    ])


def test_preprocess_json_data_core_types(
        json_data_preprocessor: Annotated[JsonDataPreprocessor, pytest.fixture]) -> None:
    data: JSON = {
        'outer_key': [
            'text',
            1,
            2.0,
            True,
            None,
            {
                'key_1': ['string', 3, 5.0, False, None],
                'key_2': ['content', 5, 6.0, True, None],
            },
            (True, False, 'maybe'),
        ],
    }
    assert json_data_preprocessor(data,) == {
        'OUTER_KEY': [
            ['MAYBE', True, False],
            {
                'KEY_1': ['None', True, '2.5', 4, 'STRING'],
                'KEY_2': ['None', False, '3.0', 6, 'CONTENT'],
            },
            'None',
            False,
            '1.0',
            2,
            'TEXT',
        ],
    }


def test_preprocess_json_data_int_enum(json_data_preprocessor) -> None:
    class Choice(IntEnum):
        Yes = 1
        No = 0

    assert json_data_preprocessor([Choice.Yes, Choice.No]) == [1, 2]


def test_preprocess_json_data_set_fail(json_data_preprocessor) -> None:
    with pytest.raises(TypeError):
        assert json_data_preprocessor(set([1, 2, 3]))
