import json.encoder
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Generator

from jsoncanon.types import FinalJson, JsonWithFinal

_orig_encode_basestring = json.encoder.encode_basestring


def _encode_basestring_with_final_json_support(s: str) -> str:
    if isinstance(s, FinalJson):
        return s
    else:
        return _orig_encode_basestring(s)


@contextmanager
def _monkey_patch_encode_basestring_with_final_json_support() -> Generator[None, None, None]:
    json.encoder.encode_basestring = _encode_basestring_with_final_json_support

    yield None

    json.encoder.encode_basestring = _orig_encode_basestring


class FinalJsonEncoder(json.encoder.JSONEncoder):
    def __init__(self, *args: Any, ensure_ascii: bool = True, **kwargs: Any):
        assert not ensure_ascii, 'FinalJsonEncoder requires ensure_ascii=False'
        super().__init__(*args, ensure_ascii=ensure_ascii, **kwargs)

    def encode(self, o: JsonWithFinal) -> str:
        with _monkey_patch_encode_basestring_with_final_json_support():
            return super().encode(o)

    def iterencode(self, o: JsonWithFinal, _one_shot: bool = False) -> Iterator[str]:
        with _monkey_patch_encode_basestring_with_final_json_support():
            return super().iterencode(o, _one_shot)
