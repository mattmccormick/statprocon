from decimal import Decimal

from typing import Union, Sequence, TypeAlias

# TODO: can replace Union with | when only supporting >= 3.10
TYPE_COUNT_VALUE: TypeAlias = Union[Decimal, int]
TYPE_MOVING_RANGE_VALUE: TypeAlias = Union[Decimal, int, None]

TYPE_COUNTS_INPUT: TypeAlias = Sequence[Union[TYPE_COUNT_VALUE, float]]
TYPE_COUNTS: TypeAlias = Sequence[TYPE_COUNT_VALUE]
TYPE_MOVING_RANGES: TypeAlias = Sequence[TYPE_MOVING_RANGE_VALUE]

TYPE_NUMERIC = Union[Decimal, float, int]
TYPE_NUMERIC_INPUTS = Sequence[Union[TYPE_NUMERIC, None]]
