import unittest

from decimal import Decimal

from statprocon import XmR


class XmRTestCase(unittest.TestCase):
    def test_empty_data(self):
        counts = []
        xmr = XmR(counts)
        mr = xmr.moving_ranges()
        self.assertEqual(mr, [])

    def test_moving_range_ints(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        mr = xmr.moving_ranges()
        self.assertEqual(mr, [None, 9, 90, 50])

    def test_moving_range_decimals(self):
        counts = [Decimal('1.25'), Decimal('10.99'), Decimal('5')]
        xmr = XmR(counts)
        mr = xmr.moving_ranges()
        self.assertEqual(mr, [None, Decimal('9.74'), Decimal('5.99')])

    def test_upper_range_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        url = xmr.upper_range_limit()
        self.assertEqual(url, Decimal('162.311'))

    def test_upper_natural_process_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        limit = xmr.upper_natural_process_limit()
        self.assertEqual(limit, Decimal('172.363'))

    def test_lower_natural_process_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        limit = xmr.lower_natural_process_limit()
        self.assertEqual(limit, Decimal('-91.863'))

    def test_verifying_software(self):
        """
        This test and dataset comes from pg 382 of Making Sense of Data:
            Data Set to Use When Verifying Software
        """

        counts = [5045, 4350, 4350, 3975, 4290, 4430, 4485, 4285, 3980, 3925, 3645, 3760, 3300, 3685, 3463, 5200]
        moving_ranges = [None, 695, 0, 375, 315, 140, 55, 200, 305, 55, 280, 115, 460, 385, 222, 1737]
        x_avg = Decimal('4135.50')
        mr_avg = Decimal('355.93')
        lnpl = Decimal('3188.72')
        unpl = Decimal('5082.28')
        url = Decimal('1163.19')

        xmr = XmR(counts)

        self.assertListEqual(xmr.moving_ranges(), moving_ranges)
        self.assertEqual(x_avg, xmr.mean(counts))
        self.assertEqual(mr_avg, round(xmr.mr_average(), 2))
        self.assertEqual(lnpl, round(xmr.lower_natural_process_limit(), 2))
        self.assertEqual(unpl, round(xmr.upper_natural_process_limit(), 2))
        self.assertEqual(url, round(xmr.upper_range_limit(), 2))

    def test_peak_flow_rates(self):
        """
        Data comes from pg 130 of "Making Sense of Data"
        Figure 9.9 XmR Chart for AM Premedication Peak Flow Rates for Days 1 to 18
        """

        x_values = [120, 140, 100, 150, 260, 150, 100, 120, 300, 300, 275, 300, 140, 170, 150, 150, 190, 180]
        mr_values = [None, 20, 40, 50, 110, 110, 50, 20, 180, 0, 25, 25, 160, 30, 20, 0, 40, 10]
        x_avg = Decimal('183.1')
        mr_avg = Decimal('52.4')

        # changes are due to rounding and using constants with 2 sig digits
        unpl = Decimal('322.3')  # 322.5 in book
        lnpl = Decimal('43.8')  # 43.7 in book
        url = Decimal('171.1')  # 171.3 in book

        xmr = XmR(x_values)

        self.assertListEqual(xmr.moving_ranges(), mr_values)
        self.assertEqual(x_avg, round(xmr.mean(x_values), 1))
        self.assertEqual(mr_avg, round(xmr.mr_average(), 1))
        self.assertEqual(lnpl, round(xmr.lower_natural_process_limit(), 1))
        self.assertEqual(unpl, round(xmr.upper_natural_process_limit(), 1))
        self.assertEqual(url, round(xmr.upper_range_limit(), 1))


if __name__ == '__main__':
    unittest.main()
