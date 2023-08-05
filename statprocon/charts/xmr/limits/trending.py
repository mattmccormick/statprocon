from decimal import Decimal
from typing import Sequence, TYPE_CHECKING

from statprocon import XmR
from statprocon.charts.xmr.constants import INVALID


class Trending(XmR):
    def __init__(self, xmr: XmR):
        self.xmr = xmr

    def __getattr__(self, item):
        """
        Delegate all other attributes to self.xmr
        """
        return getattr(self.xmr, item)

    def x_central_line(self) -> Sequence[Decimal]:
        n = len(self.xmr.counts)

        result: list[Decimal] = [INVALID] * n
        m = self._half_n()
        h = (m + self.xmr.i) // 2
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
            result[i] = result[i + 1] - s

        for i in range(h + 1, n):
            result[i] = result[i - 1] + s

        return result

    def upper_natural_process_limit(self) -> Sequence[Decimal]:
        unpl0 = self.xmr.upper_natural_process_limit()
        x_cl0 = self.xmr.x_central_line()
        delta = unpl0[0] - x_cl0[0]
        result = [x + delta for x in self.x_central_line()]
        return result
    
    def lower_natural_process_limit(self) -> Sequence[Decimal]:
        lnpl0 = self.xmr.lower_natural_process_limit()
        x_cl0 = self.xmr.x_central_line()
        delta = x_cl0[0] - lnpl0[0]
        result = [x - delta for x in self.x_central_line()]
        return result
    
    def slope(self) -> Decimal:
        """
        Returns the trend or slope of the limit and central lines
        """

        n = len(self.xmr.counts[self.xmr.i:self.xmr.j]) // 2
        nd = Decimal(str(n))

        half_average2 = sum(self.xmr.counts[(self.xmr.j-n):self.xmr.j]) / nd

        return (half_average2 - self._half_average1()) / nd

    def _half_n(self) -> int:
        return len(self.xmr.counts[self.xmr.i:self.xmr.j]) // 2

    def _half_average1(self) -> Decimal:
        n = self._half_n()
        return sum(self.xmr.counts[self.xmr.i:n]) / Decimal(str(n))
