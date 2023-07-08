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

    def x_average(self) -> Decimal:
        return self.mean(self.counts)

    def mr_average(self) -> Decimal:
        assert self.moving_ranges()[0] is None
        valid_values = cast(TYPE_COUNTS, self.moving_ranges()[1:])
        return self.mean(valid_values)

    def upper_range_limit(self) -> Decimal:
        limit = Decimal('3.268') * self.mr_average()
        return round(limit, 3)

    def upper_natural_process_limit(self) -> Decimal:
        limit = self.x_average() + (Decimal('2.660') * self.mr_average())
        return round(limit, 3)

    def lower_natural_process_limit(self) -> Decimal:
        """
        LNPL can be negative.
        It's the caller's responsibility to take max(LNPL, 0) if a negative LNPL does not make sense
        """
        limit = self.x_average() - (Decimal('2.660') * self.mr_average())
        return round(limit, 3)

    @staticmethod
    def mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))
