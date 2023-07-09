from decimal import Decimal
from typing import cast, Union, Optional

TYPE_COUNTS = list[Decimal | int]
TYPE_MOVING_RANGES = list[Decimal | int | None]


class XmR:
    def __init__(self, counts: TYPE_COUNTS):
        self.counts = counts
        self._mr: TYPE_MOVING_RANGES = []

    def moving_ranges(self) -> TYPE_MOVING_RANGES:
        if self._mr:
            return self._mr

        result: TYPE_MOVING_RANGES = []
        for i, c in enumerate(self.counts):
            if i == 0:
                result.append(None)
            else:
                value = cast(Union[Decimal | int], abs(c - self.counts[i - 1]))
                result.append(value)
        self._mr = result
        return self._mr

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

    def rule_1_x_indices_beyond_limits(
            self,
            upper_limit: Optional[Decimal] = None,
            lower_limit: Optional[Decimal] = None
    ) -> list[bool]:
        """
        Points Outside the Limits

        A single point outside the computed limits
        on either the X Chart, or the mR Chart,
        should be interpreted as an indication of
        the presence of an assignable cause which has a *dominant* effect.

        :param upper_limit: Optional - Will default to the Upper Natural Process Limit
        :param lower_limit: Optional - Will default to the Lower Natural Process Limit

        :return: list[bool] A list of boolean values of length(counts)
            True at index i means that self.counts[i] is above the upper_limit or below the lower_limit
        """

        upper = upper_limit or self.upper_natural_process_limit()
        lower = lower_limit or self.lower_natural_process_limit()

        return self._points_beyond_limits(self.counts, upper, lower)

    def rule_1_mr_indices_beyond_limits(self) -> list[bool]:
        """
        Points Outside the Limits

        A single point outside the computed limits
        on either the X Chart, or the mR Chart,
        should be interpreted as an indication of
        the presence of an assignable cause which has a *dominant* effect.

        :return: list[bool] A list of boolean values of length(self.moving_ranges())
            True at index i means that self.moving_ranges()[i] is above the Upper Range Limit
        """
        return self._points_beyond_limits(self.moving_ranges(), self.upper_range_limit())

    def rule_2_runs_about_central_line(self) -> list[bool]:
        """
        Runs About the Central Line

        Eight successive values,
        all on the same side of the central line on the X Chart
        may be interpreted as an indication of
        the presence of an assignable cause which has a *weak* but sustained effect.

        :return: list[bool] A list of boolean values of length(counts)
            True at index i means that self.counts[i] is above the line and part of a run of eight successive values
        """

        result = [False] * len(self.counts)

        # positive is number of consecutive points above the line
        # negative is number of consecutive points below the line
        central_line = 0

        avg = self.mean(self.counts)
        for i, x in enumerate(self.counts):
            if x > avg:
                if central_line < 0:
                    central_line = 1
                else:
                    central_line += 1
            elif x < avg:
                if central_line > 0:
                    central_line = -1
                else:
                    central_line -= 1

            if abs(central_line) == 8:
                for j in range(8):
                    result[i - j] = True
            elif abs(central_line) > 8:
                result[i] = True

        return result

    @staticmethod
    def _points_beyond_limits(
            data: TYPE_COUNTS | TYPE_MOVING_RANGES,
            upper_limit: Decimal,
            lower_limit: Decimal = Decimal('0')
    ) -> list[bool]:
        result = [False] * len(data)
        for i, val in enumerate(data):
            if val is None:
                continue

            if not lower_limit < val < upper_limit:
                result[i] = True

        return result

    @staticmethod
    def mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))
