from typing import Callable, TypeAlias, TypeVar

JsonScalar: TypeAlias = str | int | float | bool | None
Json: TypeAlias = JsonScalar | dict[str, 'Json'] | list['Json']
JsonWithTuple: TypeAlias = (
    JsonScalar | dict[str, 'JsonWithTuple'] | list['JsonWithTuple'] | tuple['JsonWithTuple', ...]
)
JsonType: TypeAlias = type[str | int | float | bool | dict[str, 'Json'] | list['Json']] | None

JsonWithTupleT = TypeVar('JsonWithTupleT', bound=JsonWithTuple)

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
