import unittest

from decimal import Decimal

from statprocon import XmR, XmRTrending
from statprocon.charts.xmr.constants import INVALID


class TrendingTestCase(unittest.TestCase):
    def test_trending_limits(self):
        # This data comes from pg. 179 of Making Sense of Data
        #     12.3 Charts for Each Region - Region D

        counts = [
            539, 558, 591, 556, 540, 590, 606, 643, 657, 602,
            596, 640, 691, 723, 701, 802, 749, 762, 807, 781,
        ]

        c = XmR(counts)
        xmr = XmRTrending(c)
        self.assertEqual(xmr.slope(), Decimal('13.7'))

        # Don't know exact values from the book
        cl = xmr.x_central_line()
        self.assertTrue(cl[4] < 588.2 < cl[5])
        self.assertTrue(cl[14] < 725.2 < cl[15])
        self.assertNotIn(INVALID, cl)
        self._assert_cl_deltas_equals_slope(xmr)
        # 93.5 in the book
        self._assert_limits_beyond_cl(xmr, Decimal('93.520'))

        self.assertIsInstance(xmr.to_csv(), str)

    def test_trending_limits_odd_halves(self):
        counts = [
            2.27, 2.55, 2.88, 2.27, 2.93, 3.08, 3.01,
            3.12, 3.31, 3.05, 3.54, 3.45, 3.16, 3.58,
        ]

        c = XmR(counts)
        xmr = XmRTrending(c)
        s = xmr.slope()

        self.assertEqual(s, Decimal('0.08612244897959183673469387757'))

        cl = xmr.x_central_line()
        self.assertNotIn(INVALID, cl)
        self._assert_cl_deltas_equals_slope(xmr)

    def test_negative_trending_limits(self):
        # Region B
        counts = [
            1412, 1280, 1129, 1181, 1149, 1248, 1103, 1021, 1085, 1125,
            910, 999, 883, 851, 997, 878, 939, 834, 688, 806,
        ]

        c = XmR(counts)
        xmr = XmRTrending(c)
        self.assertEqual(xmr.slope(), Decimal('-29.48'))
        cl = xmr.x_central_line()
        self.assertTrue(cl[4] > 1173.3 > cl[5])
        self.assertTrue(cl[14] > 878.4 > cl[15])
        self._assert_limits_beyond_cl(xmr, Decimal('272.161'))  # 272.2 in book

    def test_trending_limits_subset(self):
        # Region C
        counts = [
            1056, 1048, 1129, 1073, 1157, 1146, 1064, 1213, 1088, 1322,
            1256, 1132, 1352, 1353, 1466, 1196, 1330, 1003, 1197, 1337,
        ]

        c = XmR(counts, x_central_line_uses='median', subset_end_index=16)
        xmr = XmRTrending(c)
        self.assertEqual(xmr.slope(), Decimal('19.984375'))  # 19.98 in book
        cl = xmr.x_central_line()
        self.assertTrue(cl[3] < 1110.8 < cl[4])
        self.assertTrue(cl[11] < 1270.8 < cl[12])
        self._assert_limits_beyond_cl(xmr, Decimal('264.18'))  # 264.2 in book

        expected = [False] * len(counts)
        expected[17] = True
        self.assertListEqual(xmr.rule_1_x_indices_beyond_limits(), expected)

    def _assert_cl_deltas_equals_slope(self, xmr):
        cl = xmr.x_central_line()
        s = xmr.slope()
        for i, v in enumerate(cl):
            if i == 0:
                continue

            self.assertEqual(cl[i], cl[i - 1] + s)

    def _assert_limits_beyond_cl(self, xmr, delta):
        unpl = xmr.upper_natural_process_limit()
        cl = xmr.x_central_line()
        lnpl = xmr.lower_natural_process_limit()
        for u, c, l in zip(unpl, cl, lnpl):
            self.assertEqual(u - c, delta, f'UNPL: {u} - {c}')
            self.assertEqual(c - l, delta, f'LNPL: {l} - {c}')
