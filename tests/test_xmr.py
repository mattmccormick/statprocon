import unittest

from decimal import Decimal

from statprocon import XmR


class XmRTestCase(unittest.TestCase):
    def test_empty_data(self):
        counts = []
        xmr = XmR(counts)
        mr = xmr.moving_ranges()
        self.assertEqual(mr, [])

    def test_repr(self):
        counts = [3, 4, 5]
        xmr = XmR(counts)

        expected = """x_values : [3, 4, 5]
x_unpl   : [6.660, 6.660, 6.660]
x_cl     : [4.000, 4.000, 4.000]
x_lnpl   : [1.340, 1.340, 1.340]
mr_values: [None, 1, 1]
mr_url   : [3.268, 3.268, 3.268]
mr_cl    : [1.000, 1.000, 1.000]
"""
        self.assertEqual(xmr.__repr__(), expected)

    def test_to_csv(self):
        counts = [3, 4, 5]
        xmr = XmR(counts)

        expected = """x_values,x_unpl,x_cl,x_lnpl,mr_values,mr_url,mr_cl\r
3,6.660,4.000,1.340,,3.268,1.000\r
4,6.660,4.000,1.340,1,3.268,1.000\r
5,6.660,4.000,1.340,1,3.268,1.000\r
"""
        self.assertEqual(xmr.to_csv(), expected)

    def test_average_contains_one_more_exponent_as_input(self):
        counts = [3, 3, 4]
        xmr = XmR(counts)
        self.assertEqual(xmr.x_central_line(), Decimal('3.333'))

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

    def test_float_input(self):
        counts = [5.4, 3.8, 8.75, 3.6, 3, 6, 7.4, 10, 5.8, 6.6, 3, 8.8]
        xmr = XmR(counts)
        mr = xmr.moving_ranges()
        expected = [None, Decimal('1.6'), Decimal('4.95'), Decimal('5.15'), Decimal('0.6'), Decimal('3'), Decimal('1.4'), Decimal('2.6'), Decimal('4.2'), Decimal('0.8'), Decimal('3.6'), Decimal('5.8')]
        self.assertListEqual(mr, expected)

    def test_upper_range_limit(self):
        counts = [1,51, 100, 50]
        xmr = XmR(counts)
        url = xmr.upper_range_limit()
        self.assertEqual(url, Decimal('162.312'))

    def test_upper_natural_process_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        limit = xmr.upper_natural_process_limit()
        self.assertEqual(limit, Decimal('172.364'))

    def test_lower_natural_process_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        limit = xmr.lower_natural_process_limit()
        self.assertEqual(limit, Decimal('-91.864'))

    def test_limits_with_subsets(self):
        counts = [1] * 25
        counts[1] = 10
        counts[2] = 100
        counts[3] = 50

        xmr = XmR(counts, subset_end_index=24)
        self.assertEqual(xmr.upper_natural_process_limit(), Decimal('30.442'))
        self.assertEqual(xmr.upper_range_limit(), Decimal('28.134'))

        # Adjust manually so that all subset values should be 1
        xmr.i = 4
        self.assertEqual(xmr.x_central_line(), 1)
        self.assertEqual(xmr.lower_natural_process_limit(), xmr.upper_natural_process_limit())

    def test_rule_1_points_beyond_upper_limits(self):
        """
        This test dataset comes from Table 9.1: Accident Rates in Making Sense of Data
        """

        group_a = [43, 40, 37, 33, 30, 33, 34, 35, 29, 33, 31, 39]
        group_b_upper = Decimal('39.3')
        group_b_lower = Decimal('18.0')

        xmr = XmR(group_a)

        expected = [False] * len(group_a)
        for i in [0, 1]:
            expected[i] = True
        self.assertListEqual(xmr.rule_1_x_indices_beyond_limits(group_b_upper, group_b_lower), expected)

    def test_rule_1_points_beyond_lower_limits(self):
        """
        This test dataset comes from Table 9.1: Accident Rates in Making Sense of Data
        """
        group_b = [35, 37, 33, 32, 27, 29, 31, 22, 25, 30, 24, 19]
        group_a_upper = Decimal('43.9')
        group_a_lower = Decimal('25.6')

        xmr = XmR(group_b)

        expected = [False] * len(group_b)
        for i in [7, 8, 10, 11]:
            expected[i] = True
        self.assertListEqual(xmr.rule_1_x_indices_beyond_limits(group_a_upper, group_a_lower), expected)

    def test_rule_1_points_beyond_both_limits(self):
        """
        This test dataset comes from Table 9.2: Accounts Receivable for Years One and Two in Making Sense of Data
        """

        ar_pct_sales = [
            '55.6', '54.7', '54.9', '54.8', '56.9', '55.7', '53.8', '54.8', '53.4', '57.0', '59.4', '63.2',
            '60.9', '60.7', '58.6', '57.3', '56.9', '58.1', '58.3', '50.9', '53.3', '52.5', '50.8', '52.9'
        ]
        counts_dec = list(map(lambda x: Decimal(x), ar_pct_sales))
        xmr = XmR(counts_dec)

        upper_limit = Decimal('60.7')
        expected = [False] * len(ar_pct_sales)
        for i in [11, 12, 19, 22]:
            expected[i] = True

        actual = xmr.rule_1_x_indices_beyond_limits(upper_limit=upper_limit)
        self.assertListEqual(actual, expected)

        # Point 13 is detected in the chart in the book because the actual percentage is slightly lower than the limit
        self.assertFalse(actual[13], 'Point 13 equals the limit and should not be detected')

    def test_rule_1_point_beyond_upper_range_limit(self):
        """
        This test dataset also comes from Table 9.2
        """
        ar_pct_sales = ['55.6', '54.7', '54.9', '54.8', '56.9', '55.7', '53.8', '54.8', '53.4', '57.0', '59.4', '63.2',
                        '60.9', '60.7', '58.6', '57.3', '56.9', '58.1', '58.3', '50.9', '53.3', '52.5', '50.8', '52.9']
        counts_dec = list(map(lambda x: Decimal(x), ar_pct_sales))
        xmr = XmR(counts_dec)

        expected = [False] * len(ar_pct_sales)
        expected[19] = True
        self.assertListEqual(xmr.rule_1_mr_indices_beyond_limits(), expected)

    def test_rule_2(self):
        """
        This test dataset comes from Table 8.1: Percentage of High School Seniors Who Smooke Daily in Making Sense of Data
        """
        percentages = [21.3, 20.2, 20.9, 21.0, 18.8, 19.6, 18.7, 18.6, 18.1, 18.9, 19.2, 18.2, 17.3, 19.0]

        xmr = XmR(percentages)

        expected = [
            False, False, False, False, False, False,
            True, True, True, True, True, True, True, True
        ]
        self.assertListEqual(xmr.rule_2_runs_about_central_line(), expected)

    def test_rule_3(self):
        """
        Data comes from pg 130 of "Making Sense of Data"
        Figure 9.9 XmR Chart for AM Premedication Peak Flow Rates for Days 1 to 18
        @see test_peak_flow_rates
        """

        x_values = [120, 140, 100, 150, 260, 150, 100, 120, 300, 300, 275, 300, 140, 1750, 150, 150, 190, 180]
        unpl = Decimal('322.5')
        lnpl = Decimal('43.7')

        xmr = XmR(x_values)

        expected = [False] * len(x_values)
        for i in range(8, 4):
            expected[i] = True
        self.assertListEqual(xmr.rule_3_runs_near_limits(), expected)

    def test_verifying_software(self):
        """
        This test dataset comes from pg 382 of Making Sense of Data:
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
        self.assertEqual(mr_avg, round(xmr.mr_central_line(), 2))
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

        # changes are due to rounding
        unpl = Decimal('322.3')  # 322.5 in book
        lnpl = Decimal('43.8')  # 43.7 in book
        url = Decimal('171.1')  # 171.3 in book

        xmr = XmR(x_values)

        self.assertListEqual(xmr.moving_ranges(), mr_values)
        self.assertEqual(x_avg, round(xmr.mean(x_values), 1))
        self.assertEqual(mr_avg, round(xmr.mr_central_line(), 1))
        self.assertEqual(lnpl, round(xmr.lower_natural_process_limit(), 1))
        self.assertEqual(unpl, round(xmr.upper_natural_process_limit(), 1))
        self.assertEqual(url, round(xmr.upper_range_limit(), 1))
