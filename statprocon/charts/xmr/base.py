import csv
import io
import statistics

from decimal import Decimal
from typing import cast, List, Optional, Sequence, Union

from .constants import ROUNDING
from .types import (
    TYPE_COUNTS,
    TYPE_COUNTS_INPUT,
    TYPE_MOVING_RANGE_VALUE,
    TYPE_MOVING_RANGES,
    TYPE_NUMERIC_INPUTS,
)


AVERAGE = 'average'
MEDIAN = 'median'

INVALID = Decimal('NaN')

LIMITS_CONSTANT = 'constant'
LIMITS_TRENDING = 'trending'

# Scaling Factors (SF)
SF_LIMITS = {
    AVERAGE: Decimal('2.660'),
    MEDIAN: Decimal('3.145'),
}

SF_RANGES = {
    AVERAGE: Decimal('3.268'),
    MEDIAN: Decimal('3.865'),
}


class Base:
    def __init__(
            self,
            counts: TYPE_COUNTS_INPUT,
            x_central_line_uses: str = AVERAGE,
            moving_range_uses: str = AVERAGE,
            limit_type: str = LIMITS_CONSTANT,
            subset_start_index: int = 0,
            subset_end_index: Optional[int] = None,
    ):
        """

        :param counts: list of data to be used by the X chart
        :param x_central_line_uses: Whether to use the 'average' or 'median' for computing the X
            central line.  Defaults to average.  If set to median, moving_range_uses will also be
            set to median.
        :param moving_range_uses: Whether to use the 'average' or 'median' moving range.
            Defaults to average.
        :param limit_type: 'constant' or 'trending'.  If trending is specified, the X central line
            and limits will be calculated based on the slope of the trendline.  Defaults to constant
        :param subset_start_index: Optional starting index of counts to calculate limits from
        :param subset_end_index: Optional ending index of counts to calculate limits to
        """
        assert x_central_line_uses in [AVERAGE, MEDIAN]
        assert moving_range_uses in [AVERAGE, MEDIAN]

        self.counts = cast(TYPE_COUNTS, self.to_decimal_list(counts))
        self._mr: TYPE_MOVING_RANGES = []
        self.i = max(0, subset_start_index)
        self.j = len(counts)
        if subset_end_index:
            self.j = min(self.j, subset_end_index)

        assert self.i <= self.j

        self._x_central_line_uses = x_central_line_uses
        if x_central_line_uses == MEDIAN:
            self._moving_range_uses = MEDIAN
        else:
            self._moving_range_uses = moving_range_uses

        self._limit_type = limit_type

    def __repr__(self) -> str:
        result = ''
        for k, v in self.to_dict().items():
            k_format = '{0: <9}'.format(k)
            if isinstance(v, list):
                values = '[' + ', '.join(map(str, v)) + ']'
            else:
                values = v
            result += f'{k_format}: {values}\n'
        return result

    def x_to_dict(self) -> dict:
        """
        Return the values needed for the X chart as a dictionary
        """
        return {
            'values': self.counts,
            'unpl': self.upper_natural_process_limit(),
            'cl': self.x_central_line(),
            'lnpl': self.lower_natural_process_limit(),
        }

    def mr_to_dict(self) -> dict:
        """
        Return the values needed for the MR chart as a dictionary
        """
        return {
            'values': self.moving_ranges(),
            'url': self.upper_range_limit(),
            'cl': self.mr_central_line(),
        }

    def to_dict(self) -> dict:
        # Naming comes from pg. 163
        #   So Which Way Should You Compute Limits? from Making Sense of Data
        result = {}
        for k, v in self.x_to_dict().items():
            result[f'x_{k}'] = v
        for k, v in self.mr_to_dict().items():
            result[f'mr_{k}'] = v

        return result

    def to_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['x_values', 'x_unpl', 'x_cl', 'x_lnpl', 'mr_values', 'mr_url', 'mr_cl'])
        writer.writerows(zip(
            self.counts,
            self.upper_natural_process_limit(),
            self.x_central_line(),
            self.lower_natural_process_limit(),
            self.moving_ranges(),
            self.upper_range_limit(),
            self.mr_central_line()
        ))
        return output.getvalue()

    def moving_ranges(self) -> TYPE_MOVING_RANGES:
        """
        Moving ranges are the absolute differences between successive count values.
        The first element will always be None
        """
        if self._mr:
            return self._mr

        result: list[TYPE_MOVING_RANGE_VALUE] = []
        for i, c in enumerate(self.counts):
            if i == 0:
                result.append(None)
            else:
                value = cast(Union[Decimal, int], abs(c - self.counts[i - 1]))
                result.append(value)
        self._mr = result
        return self._mr

    def x_central_line(self) -> Sequence[Decimal]:
        if self._limit_type == LIMITS_CONSTANT:
            return self._x_central_line_constant()
        elif self._limit_type == LIMITS_TRENDING:
            return self._x_central_line_trending()

    def _x_central_line_constant(self) -> Sequence[Decimal]:
        valid_values = self.counts[self.i:self.j]
        if self._x_central_line_uses == AVERAGE:
            value = self._mean(valid_values)
        elif self._x_central_line_uses == MEDIAN:
            value = statistics.median(valid_values)  # type: ignore[type-var,assignment]

        return [round(value, ROUNDING)] * len(self.counts)

    def _x_central_line_trending(self) -> TYPE_COUNTS:
        n = len(self.counts)

        result: list[Decimal] = [INVALID] * n
        m = self._half_n()
        h = m // 2
        s = self.slope()

        is_odd = m % 2
        if is_odd:
            # ie. if m == 9, then insert ha1 at position 4
            # 0 1 2 3 |4| 5 6 7 8 9
            result[h] = self._half_average1()
        else:
            # ie. if m == 10, then insert ha1 at position 5 but calculate the value
            # based on half the slope
            # since the mid point is halfway between 4 and 5
            # 0 1 2 3 4 | 5 6 7 8 9
            result[h] = self._half_average1() + Decimal('0.5') * s

        for i in reversed(range(0, h)):
            result[i] = result[i+1] - s

        for i in range(h+1, n):
            result[i] = result[i-1] + s

        return result

    def mr_central_line(self) -> Sequence[Decimal]:
        mr = self.moving_ranges()
        assert mr[0] is None
        valid_values = cast(TYPE_COUNTS, mr[self.i + 1:self.j])

        if self._moving_range_uses == AVERAGE:
            value = self._mean(valid_values)
        elif self._moving_range_uses == MEDIAN:
            # mypy gives the error:
            #   Value of type variable "_NumberT" of "median" cannot be "Decimal | int"
            # However, the [statistics library](https://docs.python.org/3/library/statistics.html)
            # says that the functions support int and Decimal
            # When ignoring type-var, an assignment error appears:
            #   Incompatible types in assignment (expression has type "Decimal | int", variable has type "Decimal")
            # But the variable can be int and not necessarily Decimal
            value = statistics.median(valid_values)  # type: ignore[type-var,assignment]

        return [round(value, ROUNDING)] * len(mr)

    def upper_range_limit(self) -> Sequence[Decimal]:
        sf = SF_RANGES[self._moving_range_uses]
        mr_cl = self.mr_central_line()
        limit = sf * mr_cl[0]
        value = round(limit, ROUNDING)
        return [value] * len(mr_cl)

    def upper_natural_process_limit(self) -> Sequence[Decimal]:
        if self._limit_type == LIMITS_CONSTANT:
            return self._upper_natural_process_limit_constant()
        elif self._limit_type == LIMITS_TRENDING:
            return self._upper_natural_process_limit_trending()

    def _upper_natural_process_limit_constant(self) -> Sequence[Decimal]:
        sf = SF_LIMITS[self._moving_range_uses]
        limit = self._x_central_line_constant()[0] + (sf * self.mr_central_line()[0])
        value = round(limit, ROUNDING)
        return [value] * len(self.counts)

    def _upper_natural_process_limit_trending(self) -> Sequence[Decimal]:
        unpl_constant = self._upper_natural_process_limit_constant()
        x_cl_bar = self._x_central_line_constant()
        delta = unpl_constant[0] - x_cl_bar[0]
        result = [x + delta for x in self._x_central_line_trending()]
        return result

    def lower_natural_process_limit(self) -> Sequence[Decimal]:
        """
        LNPL can be negative.
        It's the caller's responsibility to take max(LNPL, 0) if a negative LNPL does not make sense
        """
        if self._limit_type == LIMITS_CONSTANT:
            return self._lower_natural_process_limit_constant()
        elif self._limit_type == LIMITS_TRENDING:
            return self._lower_natural_process_limit_trending()

    def _lower_natural_process_limit_constant(self) -> Sequence[Decimal]:
        sf = SF_LIMITS[self._moving_range_uses]
        limit = self._x_central_line_constant()[0] - (sf * self.mr_central_line()[0])
        value = round(limit, ROUNDING)
        return [value] * len(self.counts)

    def _lower_natural_process_limit_trending(self) -> Sequence[Decimal]:
        lnpl_constant = self._lower_natural_process_limit_constant()
        x_cl_bar = self._x_central_line_constant()
        delta = x_cl_bar[0] - lnpl_constant[0]
        result = [x - delta for x in self._x_central_line_trending()]
        return result

    def slope(self) -> Decimal:
        """
        Returns the trend or slope of the limit and central lines
        """

        if self._limit_type == LIMITS_CONSTANT:
            return Decimal('0')

        n = len(self.counts) // 2
        nd = Decimal(str(n))

        half_average2 = sum(self.counts[-n:]) / nd

        return (half_average2 - self._half_average1()) / nd

    def _half_average1(self) -> Decimal:
        n = self._half_n()
        return sum(self.counts[0:n]) / Decimal(str(n))

    def _half_n(self) -> int:
        return len(self.counts) // 2

    def rule_1_x_indices_beyond_limits(
            self,
            upper_limit: Optional[Decimal] = None,
            lower_limit: Optional[Decimal] = None,
    ) -> List[bool]:
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
        n = len(self.counts)
        upper = self.upper_natural_process_limit()
        if upper_limit:
            upper = [upper_limit] * n

        lower = self.lower_natural_process_limit()
        if lower_limit:
            lower = [lower_limit] * n

        return self._points_beyond_limits(self.counts, upper, lower)

    def rule_1_mr_indices_beyond_limits(self) -> List[bool]:
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

    def rule_2_runs_about_central_line(self) -> List[bool]:
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
        run = 0
        for i, (x, cl) in enumerate(zip(self.counts, self.x_central_line())):
            if x > cl:
                if run < 0:
                    run = 1
                else:
                    run += 1
            elif x < cl:
                if run > 0:
                    run = -1
                else:
                    run -= 1

            if abs(run) == 8:
                for j in range(8):
                    result[i - j] = True
            elif abs(run) > 8:
                result[i] = True

        return result

    def rule_3_runs_near_limits(self) -> List[bool]:
        """
        Runs Near the Limits

        Three out of four successive values on the X Chart
        all within the upper 25% of the region between the limits, or
        all within the lower 25% of the region between the limits,
        may be interpreted as an indication of the presence
        of an assignable cause which has a *moderate* but sustained effect.
        """
        result = [False] * len(self.counts)

        # positive value is point near upper limit
        # negative value is point near lower limit
        near_limits = [0] * len(self.counts)

        values = zip(self.counts, self.upper_natural_process_limit(), self.lower_natural_process_limit())
        for i, (x, unpl, lnpl) in enumerate(values):
            upper_25 = ((unpl - lnpl) * Decimal('.75')) + lnpl
            lower_25 = ((unpl - lnpl) * Decimal('.25')) + lnpl
            if x < lower_25:
                near_limits[i] = -1

            if x > upper_25:
                near_limits[i] = 1

            if i >= 3:
                successive_values = near_limits[i - 3:i + 1]
                if abs(sum(successive_values)) >= 3:
                    for j in range(i - 3, i + 1):
                        result[j] = True

        return result

    @staticmethod
    def _points_beyond_limits(
            data: TYPE_MOVING_RANGES,
            upper_limits: Sequence[Decimal],
            lower_limits: Optional[Sequence[Decimal]] = None
    ) -> List[bool]:
        result = [False] * len(data)

        if lower_limits is None:
            lower_limits = [Decimal('-Inf')] * len(upper_limits)

        for i, (x, w, y) in enumerate(zip(data, lower_limits, upper_limits)):
            if x is None:  # first index of Moving Ranges
                continue

            if not w <= x <= y:
                result[i] = True

        return result

    @staticmethod
    def _mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))

    @staticmethod
    def to_decimal_list(values: TYPE_NUMERIC_INPUTS) -> TYPE_MOVING_RANGES:
        result: List[Union[Decimal, None]] = []
        for x in values:
            if x is None:
                result.append(None)
            else:
                result.append(Decimal(str(x)))
        return result
