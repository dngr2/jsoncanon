from types import GenericAlias
from typing import get_origin


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
