from decimal import Decimal
from typing import Sequence

from statprocon.charts.xmr.types import TYPE_COUNTS
from statprocon.charts.xmr.constants import ROUNDING


class Average:
    def __init__(self, counts, i ,j):
        self.counts = counts
        self.i = i
        self.j = j

    def x(self) -> Sequence[Decimal]:
        avg = self.mean(self.counts[self.i:self.j])
        value = round(avg, ROUNDING)
        return [value] * len(self.counts)

    @staticmethod
    def mean(nums: TYPE_COUNTS) -> Decimal:
        s = sum(nums)
        n = len(nums)
        return Decimal(str(s)) / Decimal(str(n))
