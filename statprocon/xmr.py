from decimal import Decimal
from typing import cast, Union

TYPE_COUNTS = list[Decimal | int]
TYPE_MOVING_RANGES = list[Decimal | int | None]


class XmR:
    def __init__(self, counts: TYPE_COUNTS):
        self.counts = counts
        self.mr = None

    def moving_ranges(self) -> TYPE_MOVING_RANGES:
        if self.mr is not None:
            return self.mr

        result: list[Decimal | int | None] = []
        for i, c in enumerate(self.counts):
            if i == 0:
                result.append(None)
            else:
                value = cast(Union[Decimal | int], abs(c - self.counts[i - 1]))
                result.append(value)
        self.mr = result
        return self.mr
