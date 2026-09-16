import json
from typing import cast, overload

from jsoncanon.functions import (
    dict_to_sorted_by_utf16_tuple,
    float_to_int_if_whole_and_not_large_exp,
    int_to_str_if_too_large,
)
from jsoncanon.util import (
    JsonDataPreprocessor,
    JsonScalar,
    JsonWithTuple,
    JsonWithTupleT,
)


@overload
def canonicalize(data: dict[str, JsonWithTupleT]) -> bytes: ...


@overload
def canonicalize(data: list[JsonWithTupleT]) -> bytes: ...


@overload
def canonicalize(data: tuple[JsonWithTupleT, ...]) -> bytes: ...


@overload
def canonicalize(data: JsonScalar) -> bytes: ...


@overload
def canonicalize(data: JsonWithTuple) -> bytes: ...


def canonicalize(data: object) -> bytes:
    return _canonicalize(cast(JsonWithTuple, data))


def _canonicalize(data: JsonWithTuple) -> bytes:
    preprocess = JsonDataPreprocessor(
        [
            int_to_str_if_too_large,
            float_to_int_if_whole_and_not_large_exp,
            dict_to_sorted_by_utf16_tuple,
        ]
    )
    preprocessed_data = preprocess(data)
    output = json.dumps(
        preprocessed_data,
        separators=(',', ':'),
        ensure_ascii=False,
        allow_nan=False,
    )
    return output.encode('utf8')
