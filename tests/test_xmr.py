import unittest

from decimal import Decimal

from statprocon import XmR
from statprocon.charts.xmr.types import TYPE_COUNT_VALUE


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

    def test_to_dict_includes_halfway_lines(self):
        counts = [3, 4, 5]
        xmr = XmR(counts)

        d = xmr.to_dict(include_halfway_lines=True)
        self._assert_line_equals(d['x_unpl_mid'], Decimal('5.33'))
        self._assert_line_equals(d['x_lnpl_mid'], Decimal('2.67'))

    def test_to_dict_moving_average(self):
        counts = [1, 2, 3, 4, 5, 6, 7]
        xmr = XmR(counts)

        d = xmr.to_dict(moving_average_points=4)
        expected = [None, None, None, 2.5, 3.5, 4.5, 5.5]
        self.assertListEqual(d['x_moving_average'], expected)

    def test_to_dict_lnpl_floor(self):
        counts = [1, 2, 3, 4]
        xmr = XmR(counts, limit_floor=0)

        d = xmr.x_to_dict()
        self.assertNotIn('lnpl', d)

    def test_average_contains_one_more_exponent_as_input(self):
        counts = [3, 3, 4]
        xmr = XmR(counts)
        self._assert_func_output_equals_line(xmr, 'x_central_line', Decimal('3.333'))

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
        expected = xmr.to_decimal_list([None, 1.6, 4.95, 5.15, 0.6, 3, 1.4, 2.6, 4.2, 0.8, 3.6, 5.8])
        self.assertListEqual(mr, expected)

    def test_upper_range_limit(self):
        counts = [1,51, 100, 50]
        xmr = XmR(counts)
        self._assert_func_output_equals_line(xmr, 'upper_range_limit', Decimal('162.312'))

    def test_upper_natural_process_limit(self):
        counts = [1, 10, 100, 50]
        xmr = XmR(counts)
        self._assert_func_output_equals_line(xmr, 'upper_natural_process_limit', Decimal('172.364'))

    def test_limits_with_subsets(self):
        counts = [1] * 25
        counts[1] = 10
        counts[2] = 100
        counts[3] = 50

        xmr = XmR(counts, subset_start_index=4, subset_end_index=24)
        self._assert_func_output_equals_line(xmr, 'upper_natural_process_limit', Decimal('1.000'))
        self._assert_func_output_equals_line(xmr, 'upper_range_limit', Decimal('0'))
        self._assert_func_output_equals_line(xmr, 'x_central_line', 1)
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
            '60.9', '60.7', '58.6', '57.3', '56.9', '58.1', '58.3', '50.9', '53.3', '52.5', '50.8', '52.9',
        ]
        xmr = XmR(ar_pct_sales)

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
        ar_pct_sales = [
            '55.6', '54.7', '54.9', '54.8', '56.9', '55.7', '53.8', '54.8', '53.4', '57.0', '59.4', '63.2',
            '60.9', '60.7', '58.6', '57.3', '56.9', '58.1', '58.3', '50.9', '53.3', '52.5', '50.8', '52.9',
        ]
        xmr = XmR(ar_pct_sales)

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
        self.assertEqual(x_avg, xmr.x_central_line()[0])
        self.assertEqual(mr_avg, round(xmr.mr_central_line()[0], 2))
        self.assertEqual(lnpl, round(xmr.lower_natural_process_limit()[0], 2))
        self.assertEqual(unpl, round(xmr.upper_natural_process_limit()[0], 2))
        self.assertEqual(url, round(xmr.upper_range_limit()[0], 2))

    def test_peak_flow_rates(self):
        """
        Data comes from pg 130 of "Making Sense of Data"
        Figure 9.9 XmR Chart for AM Premedication Peak Flow Rates for Days 1 to 18
        """

        x_values = [120, 140, 100, 150, 260, 150, 100, 120, 300, 300, 275, 300, 140, 170, 150, 150, 190, 180]
        mr_values = [None, 20, 40, 50, 110, 110, 50, 20, 180, 0, 25, 25, 160, 30, 20, 0, 40, 10]
        x_cl = Decimal('183.1')
        mr_cl = Decimal('52.4')

        # changes are due to rounding
        unpl = Decimal('322.3')  # 322.5 in book
        lnpl = Decimal('43.8')  # 43.7 in book
        url = Decimal('171.1')  # 171.3 in book

        xmr = XmR(x_values)

        self.assertListEqual(xmr.moving_ranges(), mr_values)
        self.assertEqual(x_cl, round(xmr.x_central_line()[0], 1))
        self.assertEqual(mr_cl, round(xmr.mr_central_line()[0], 1))
        self.assertEqual(lnpl, round(xmr.lower_natural_process_limit()[0], 1))
        self.assertEqual(unpl, round(xmr.upper_natural_process_limit()[0], 1))
        self.assertEqual(url, round(xmr.upper_range_limit()[0], 1))

    def test_median_moving_range(self):
        # Data comes from pg. 145 of Making Sense of Data
        # Section 10.2 Using the Median Moving Range
        x_values = [2.5, 2.3, 16.3, 6.3, 7.6, 16.3, 7.1, 7.8, 7.8, 9.9, 10.5, -4.8]
        mr_values = [None, 0.2, 14, 10, 1.3, 8.7, 9.2, 0.7, 0, 2.1, 0.6, 15.3]
        x_cl = Decimal('7.467')  # 7.47 in book
        mr_cl = Decimal('2.10')
        unpl = Decimal('14.072')  # 14.07 in book
        lnpl = Decimal('0.862')  # 0.87 in book
        url = Decimal('8.116')  # 8.12 in book

        xmr = XmR(x_values, moving_range_uses='median')

        self.assertListEqual(xmr.moving_ranges(), xmr.to_decimal_list(mr_values))
        self.assertEqual(x_cl, xmr.x_central_line()[0])
        self.assertEqual(mr_cl, xmr.mr_central_line()[0])
        self.assertEqual(lnpl, xmr.lower_natural_process_limit()[0])
        self.assertEqual(unpl, xmr.upper_natural_process_limit()[0])
        self.assertEqual(url, xmr.upper_range_limit()[0])

    def test_median_x_central_line(self):
        # Data comes from pg. 147 of Making Sense of Data
        # s10.2 Episode Treatment Groups
        x_values = [
            260, 130, 189, 1080, 175, 200, 193, 120, 33,
            293, 195, 571, 55698, 209, 1825, 239, 290, 254,
            93, 278, 185, 123, 9434, 408, 570, 118, 238,
            207, 153, 209, 243, 110, 306, 343, 244,
        ]
        x_cl = 238
        mr_cl = 125
        unpl = 631.125  # 630 in book
        lnpl = -155.125  # -154 in book
        url = 483.125  # 482 in book

        xmr = XmR(x_values, x_central_line_uses='median')

        self.assertEqual(x_cl, xmr.x_central_line()[0])
        self.assertEqual(mr_cl, xmr.mr_central_line()[0])
        self.assertEqual(lnpl, xmr.lower_natural_process_limit()[0])
        self.assertEqual(unpl, xmr.upper_natural_process_limit()[0])
        self.assertEqual(url, xmr.upper_range_limit()[0])

    def _assert_func_output_equals_line(self, xmr: XmR, func: str, value: TYPE_COUNT_VALUE):
        actual = getattr(xmr, func)()
        self._assert_line_equals(actual, value)

    def _assert_line_equals(self, actual: list, expected_value: TYPE_COUNT_VALUE):
        self.assertListEqual(actual, [expected_value] * len(actual))
