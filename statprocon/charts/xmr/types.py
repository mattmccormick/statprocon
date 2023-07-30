from decimal import Decimal

from packaging.markers import Marker
from typing import Union, Sequence

py310 = Marker('python_version >= "3.10"')
if py310.evaluate():
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

# TODO: can replace Union with | when only supporting >= 3.10
TYPE_COUNT_VALUE: TypeAlias = Union[Decimal, int]
TYPE_MOVING_RANGE_VALUE: TypeAlias = Union[Decimal, int, None]

TYPE_COUNTS_INPUT: TypeAlias = Sequence[Union[TYPE_COUNT_VALUE, float]]
TYPE_COUNTS: TypeAlias = Sequence[TYPE_COUNT_VALUE]
TYPE_MOVING_RANGES: TypeAlias = Sequence[TYPE_MOVING_RANGE_VALUE]

TYPE_NUMERIC_INPUTS = Sequence[Union[Decimal, float, int, None]]
