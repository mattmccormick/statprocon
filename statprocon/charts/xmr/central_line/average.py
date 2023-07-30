from decimal import Decimal
from typing import cast, Sequence

from statprocon.charts.xmr.types import TYPE_COUNTS, TYPE_MOVING_RANGES
from statprocon.charts.xmr.constants import ROUNDING


class Average:
    """
    Compute the central line for X and MR charts using the average
    """
    def __init__(self, counts, i ,j):
        self.counts = counts
        self.i = i
        self.j = j

    def x(self) -> Sequence[Decimal]:
        avg = self.mean(self.counts[self.i:self.j])
        value = round(avg, ROUNDING)
        return [value] * len(self.counts)

    def mr(self, moving_ranges: TYPE_MOVING_RANGES) -> Sequence[Decimal]:
        assert moving_ranges[0] is None
        valid_values = cast(TYPE_COUNTS, moving_ranges[self.i+1:self.j])
        avg = self.mean(valid_values)
        return [round(avg, ROUNDING)] * len(moving_ranges)

    @staticmethod
    def mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))
