from collections import defaultdict
from dataclasses import dataclass
from inspect import Parameter, signature, Signature
from types import GenericAlias, NoneType, UnionType
from typing import (Any,
                    Callable,
                    cast,
                    Dict,
                    Generic,
                    get_args,
                    get_origin,
                    List,
                    NamedTuple,
                    Optional,
                    Tuple,
                    Type,
                    TypeAlias,
                    TypeVar,
                    Union)

JSON_Dict = Dict[str, 'JSON']
JSON_List = List['JSON']
JSON_List_or_Tuple = Union[List['JSON'], Tuple['JSON', ...]]
JSON = Union[JSON_Dict, JSON_List_or_Tuple, str, int, float, bool, NoneType]
JSON_Type = Type[Union[str, int, float, bool, None, Dict, List]]


def ensure_plain_type(in_type: type | GenericAlias) -> type:
    """Normalize a type form to its plain runtime representative.

    Args:
        in_type: Type expression.

    Returns:
        The generic origin for parametrized types or the original
        value when it is already plain.
    """

    return get_origin(in_type) if get_args(in_type) else in_type


PreprocInputType: TypeAlias = JSON
PreprocReturnType: TypeAlias = JSON
PreprocFunc = Callable[[PreprocInputType], PreprocReturnType]


@dataclass
class PreprocFuncInfo:
    input_type: type[PreprocInputType]
    return_type: type[PreprocReturnType]
    func: PreprocFunc


@dataclass
class JsonDataPreprocessor:
    def __init__(self, preprocess_funcs: List[PreprocFunc] = []):
        self._preprocess_func_info_dict: defaultdict[type[JSON],
                                                     List[PreprocFuncInfo]] = defaultdict(list)
        for preproc_func in preprocess_funcs:
            func_sign = signature(preproc_func)
            input_type = self._validate_params_and_get_input_type(func_sign, preproc_func)
            return_type = self._validate_and_get_return_type(func_sign, preproc_func)

            self._preprocess_func_info_dict[input_type].append(
                PreprocFuncInfo(input_type, return_type, preproc_func))

    def _validate_and_get_return_type(self, func_sign: Signature, preproc_func: PreprocFunc) -> Any:
        return_type = func_sign.return_annotation
        assert return_type is not Parameter.empty, (
            f'Preprocess function {preproc_func.__name__} must have a return annotation')

        return ensure_plain_type(return_type)

    def _validate_params_and_get_input_type(
        self,
        func_sign: Signature,
        preproc_func: PreprocFunc,
    ) -> Any:
        assert len(func_sign.parameters) == 1, (
            f'Preprocess function {preproc_func.__name__} must have exactly one parameter')

        input_param: Parameter = tuple(func_sign.parameters.values())[0]
        assert input_param.kind == Parameter.POSITIONAL_ONLY, (
            f'Preprocess function {preproc_func.__name__} parameter must be positional only')

        input_annotation = input_param.annotation
        assert input_annotation is not Parameter.empty, (
            f'Preprocess function {preproc_func.__name__} parameter must have type annotation')

        return ensure_plain_type(input_annotation)

    def __call__(self, data: JSON) -> JSON:
        match data:
            case str():
                data = self._preprocess_for_type(data, str)
            case bool():
                data = self._preprocess_for_type(data, bool)
            case int():
                data = self._preprocess_for_type(data, int)
            case float():
                data = self._preprocess_for_type(data, float)
            case NoneType():
                data = self._preprocess_for_type(data, NoneType)
            case dict():
                data = {key: self(val) for (key, val) in data.items()}
                data = self._preprocess_for_type(data, dict)
            case list() | tuple():
                data = [self(val) for val in data]
                data = self._preprocess_for_type(data, list)
            case _:
                raise TypeError(f'Object of type "{type(data)}" not supported')
        return data

    def _preprocess_for_type(self, data: JSON, data_type: JSON_Type) -> JSON_Type:
        for preproc_func_info in self._preprocess_func_info_dict[data_type]:
            data = preproc_func_info.func(data)
        return data
