from collections import defaultdict
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from types import GenericAlias
from typing import (
    Any,
    Callable,
    TypeAlias,
    cast,
    get_origin,
    overload,
)

from typing_extensions import TypeVar

JsonScalar: TypeAlias = str | int | float | bool | None

JsonWithTupleJson: TypeAlias = JsonScalar | dict[str, 'Json'] | list['Json']
Json: TypeAlias = JsonScalar | dict[str, 'Json'] | list['Json']
JsonWithTuple: TypeAlias = (
    JsonScalar | dict[str, 'JsonWithTuple'] | list['JsonWithTuple'] | tuple['JsonWithTuple', ...]
)
JsonType: TypeAlias = type[str | int | float | bool | dict[str, 'Json'] | list['Json']] | None

JsonWithTupleT = TypeVar('JsonWithTupleT', bound=JsonWithTuple)


def ensure_plain_type(in_type: type | GenericAlias) -> type:
    """Normalize a type form to its plain runtime representative.

    Args:
        in_type: Type expression.

    Returns:
        The generic origin for parametrized types or the original
        value when it is already plain.
    """

    if isinstance(in_type, GenericAlias):
        return get_origin(in_type)
    else:
        return in_type


PreprocInputType: TypeAlias = Json
PreprocReturnType: TypeAlias = Json
PreprocFunc: TypeAlias = Callable[[PreprocInputType], PreprocReturnType]

# Each preprocess function accepts exactly one of the runtime JSON member
# types (never the full JSON union), so the alias is expressed as a union of
# callable shapes.
PreprocInputFunc: TypeAlias = (
    Callable[[str], PreprocReturnType]
    | Callable[[bool], PreprocReturnType]
    | Callable[[int], PreprocReturnType]
    | Callable[[float], PreprocReturnType]
    | Callable[[None], PreprocReturnType]
    | Callable[[dict[str, Json]], PreprocReturnType]
    | Callable[[list[Json]], PreprocReturnType]
)


@dataclass
class PreprocFuncInfo:
    input_type: type[PreprocInputType]
    return_type: type[PreprocReturnType]
    func: PreprocFunc


@dataclass
class JsonDataPreprocessor:
    def __init__(self, preprocess_funcs: list[PreprocInputFunc] | None = None):
        if preprocess_funcs is None:
            preprocess_funcs = []

        self._preproc_func_info_dict: defaultdict[JsonType, list[PreprocFuncInfo]] = defaultdict(
            list
        )
        for preproc_func in preprocess_funcs:
            func_sign = signature(preproc_func)
            input_type = self._validate_params_and_get_input_type(func_sign, preproc_func)
            return_type = self._validate_and_get_return_type(func_sign, preproc_func)

            self._preproc_func_info_dict[input_type].append(
                PreprocFuncInfo(input_type, return_type, cast(PreprocFunc, preproc_func))
            )

    @staticmethod
    def _validate_and_get_return_type(func_sign: Signature, preproc_func: PreprocInputFunc) -> Any:
        return_type = func_sign.return_annotation
        assert return_type is not Parameter.empty, (
            f'Preprocess function {preproc_func.__name__} must have a return annotation'
        )

        return ensure_plain_type(return_type)

    @staticmethod
    def _validate_params_and_get_input_type(
        func_sign: Signature,
        preproc_func: PreprocInputFunc,
    ) -> Any:
        assert len(func_sign.parameters) == 1, (
            f'Preprocess function {preproc_func.__name__} must have exactly one parameter'
        )

        input_param: Parameter = tuple(func_sign.parameters.values())[0]
        assert input_param.kind == Parameter.POSITIONAL_ONLY, (
            f'Preprocess function {preproc_func.__name__} parameter must be positional only'
        )

        input_annotation = input_param.annotation
        assert input_annotation is not Parameter.empty, (
            f'Preprocess function {preproc_func.__name__} parameter must have type annotation'
        )

        return ensure_plain_type(input_annotation)

    @overload
    def __call__(self, data: dict[str, JsonWithTupleT]) -> Json: ...

    @overload
    def __call__(self, data: list[JsonWithTupleT]) -> Json: ...

    @overload
    def __call__(self, data: tuple[JsonWithTupleT, ...]) -> Json: ...

    @overload
    def __call__(self, data: JsonScalar) -> Json: ...

    @overload
    def __call__(self, data: JsonWithTuple) -> Json: ...

    def __call__(self, data: object) -> Json:
        return self._preprocess(cast(JsonWithTuple, data))

    def _preprocess(self, data: JsonWithTuple) -> Json:
        output: Json
        match data:
            case str():
                output = self._preprocess_for_type(data, str)
            case bool():
                output = self._preprocess_for_type(data, bool)
            case int():
                output = self._preprocess_for_type(data, int)
            case float():
                output = self._preprocess_for_type(data, float)
            case None:
                output = self._preprocess_for_type(data, None)
            case dict():
                output = {key: self._preprocess(val) for (key, val) in data.items()}
                output = self._preprocess_for_type(output, dict)
            case list() | tuple():
                output = [self._preprocess(val) for val in data]
                output = self._preprocess_for_type(output, list)
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise TypeError(f'Object of type "{type(data)}" not supported')
        return output

    def _preprocess_for_type(self, data: Json, data_type: JsonType) -> Json:
        preproc_funcs_for_data_type = self._preproc_func_info_dict[data_type]
        for preproc_func_info in preproc_funcs_for_data_type:
            data = preproc_func_info.func(data)
        return data
