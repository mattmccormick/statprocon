from decimal import Decimal
from typing import cast, Union, Optional

TYPE_COUNTS = list[Decimal | int]
TYPE_MOVING_RANGES = list[Decimal | int | None]


class XmR:
    def __init__(self, counts: TYPE_COUNTS):
        self.counts = counts
        self.mr: TYPE_MOVING_RANGES = []

    def moving_ranges(self) -> TYPE_MOVING_RANGES:
        if self.mr:
            return self.mr

        result: TYPE_MOVING_RANGES = []
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

    def x_indices_beyond_limits(
            self,
            upper_limit: Optional[Decimal] = None,
            lower_limit: Optional[Decimal] = None
    ) -> set[int]:
        """
        Points Outside the Limits

        A single point outside the computed limits
        on either the X Chart, or the mR Chart,
        should be interpreted as an indication of
        the presence of an assignable cause which has a *dominant* effect.

        :return: set[int] Returns a set of the indices of counts that are beyond the Upper and Lower Natural Process Limits
        """

        upper = upper_limit or self.upper_natural_process_limit()
        lower = lower_limit or self.lower_natural_process_limit()

        return self._points_beyond_limits(self.counts, upper, lower)

    def mr_indices_beyond_limits(self) -> set[int]:
        """
        Points Outside the Limits

        A single point outside the computed limits
        on either the X Chart, or the mR Chart,
        should be interpreted as an indication of
        the presence of an assignable cause which has a *dominant* effect.

        :return: set[int] Returns a set of the indices of moving ranges that are beyond the Upper Range Limit
        """
        return self._points_beyond_limits(self.moving_ranges(), self.upper_range_limit())

    def _points_beyond_limits(
            self,
            data: TYPE_COUNTS | TYPE_MOVING_RANGES,
            upper_limit: Decimal,
            lower_limit: Decimal = Decimal('0')
    ) -> set:
        result = set()
        for i, val in enumerate(data):
            if val is None:
                continue

            if not lower_limit < val < upper_limit:
                result.add(i)

        return result

    @staticmethod
    def mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))
