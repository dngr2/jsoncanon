from typing import Callable, TypeAlias, TypeVar

JsonScalar: TypeAlias = str | int | float | bool | None
Json: TypeAlias = JsonScalar | dict[str, 'Json'] | list['Json']
JsonType: TypeAlias = type[str | int | float | bool | dict[str, 'Json'] | list['Json']] | None

JsonWithTuple: TypeAlias = (
    JsonScalar | dict[str, 'JsonWithTuple'] | list['JsonWithTuple'] | tuple['JsonWithTuple', ...]
)
JsonWithTupleT = TypeVar('JsonWithTupleT', bound=JsonWithTuple)


class FinalJson(str): ...


JsonScalarWithFinal: TypeAlias = JsonScalar | FinalJson
JsonWithFinal: TypeAlias = JsonScalarWithFinal | dict[str, 'JsonWithFinal'] | list['JsonWithFinal']

PreprocFunc: TypeAlias = Callable[[JsonWithFinal], JsonWithFinal]

# Each preprocess function accepts exactly one of the runtime JSON member
# types (never the full JSON union), so the alias is expressed as a union of
# callable shapes.
PreprocInputFunc: TypeAlias = (
    Callable[[str], JsonWithFinal]
    | Callable[[bool], JsonWithFinal]
    | Callable[[int], JsonWithFinal]
    | Callable[[float], JsonWithFinal]
    | Callable[[None], JsonWithFinal]
    | Callable[[dict[str, JsonWithFinal]], JsonWithFinal]
    | Callable[[list[JsonWithFinal]], JsonWithFinal]
)
