from decimal import Decimal
from typing import Sequence, Union

from statprocon import XmR
from statprocon.charts.xmr.constants import INVALID


class Trending(XmR):
    def __init__(self, xmr: XmR):
        """
        This class will compute limits that trend upwards or downwards over time based on the slope
        of the average of the two halves of count data.
        When you have XmR charts that trend upwards or downwards over time, it's better to use
        trended limits for use with detection rules and forecasting.

        :param xmr: The constant limits XmR chart to use as a basis for computing trending limits
        """
        self.xmr = xmr
        self.i = self.xmr.i
        self.j = self.xmr.j

    def __getattr__(self, item):
        """
        Delegate all other attributes to self.xmr
        """
        return getattr(self.xmr, item)

    def x_central_line(self) -> Sequence[Decimal]:
        n = len(self.xmr.counts)

        result: list[Decimal] = [INVALID] * n
        m = self._half_n()
        h = m // 2 + self.i
        s = self.slope()

        is_odd = m % 2
        if is_odd:
            # i.e. if m == 9, then insert ha1 at position 4
            # 0 1 2 3 |4| 5 6 7 8 9
            result[h] = self._half_average1()
        else:
            # i.e. if m == 10, then insert ha1 at position 5 but calculate the value
            # based on half the slope
            # since the midpoint is halfway between 4 and 5
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

    def lower_natural_process_limit(self, floor: Union[Decimal, int, float] = Decimal('-Infinity')) -> Sequence[Decimal]:
        lnpl0 = self.xmr.lower_natural_process_limit()
        x_cl0 = self.xmr.x_central_line()
        delta = x_cl0[0] - lnpl0[0]
        result = [max(x - delta, Decimal(str(floor))) for x in self.x_central_line()]
        return result

    def slope(self) -> Decimal:
        """
        Returns the trend or slope of the limit and central lines
        """

        n = len(self.xmr.counts[self.i:self.j]) // 2
        nd = Decimal(str(n))

        half_average2 = sum(self.xmr.counts[(self.j-n):self.j]) / nd
        half_average1 = self._half_average1()

        result = (half_average2 - half_average1) / nd
        return result

    def _half_n(self) -> int:
        return len(self.xmr.counts[self.i:self.j]) // 2

    def _half_average1(self) -> Decimal:
        n = self._half_n()
        result = sum(self.xmr.counts[self.i:self.i+n]) / Decimal(str(n))
        return result
