from decimal import Decimal

from typing import Sequence, TypeAlias

TYPE_COUNT_VALUE: TypeAlias = Decimal | int
TYPE_MOVING_RANGE_VALUE: TypeAlias = Decimal | int | None

TYPE_COUNTS_INPUT: TypeAlias = Sequence[TYPE_COUNT_VALUE | float]
TYPE_COUNTS: TypeAlias = Sequence[TYPE_COUNT_VALUE]
TYPE_MOVING_RANGES: TypeAlias = Sequence[TYPE_MOVING_RANGE_VALUE]

TYPE_NUMERIC = Decimal | float | int
TYPE_NUMERIC_INPUTS = Sequence[TYPE_NUMERIC | None]
