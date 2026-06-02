import importlib.util
import unittest

from unittest import mock

from statprocon import XmR


HAS_PLOT_DEPS = (
    importlib.util.find_spec('pandas') is not None
    and importlib.util.find_spec('matplotlib') is not None
)

if HAS_PLOT_DEPS:
    import matplotlib

    # Use a non-interactive backend so the tests run without a display.
    matplotlib.use('Agg')


@unittest.skipUnless(HAS_PLOT_DEPS, 'requires the [plot] extra (pandas + matplotlib)')
class PlotTestCase(unittest.TestCase):
    # A stable process with a single large spike that breaches the limits,
    # so the detection-rule markers are exercised.
    counts = [5, 5, 5, 5, 5, 5, 5, 5, 5, 100]

    def tearDown(self):
        import matplotlib.pyplot as plt

        plt.close('all')

    @staticmethod
    def _line_labels(ax):
        return {line.get_label() for line in ax.get_lines()}

    def test_x_plot_returns_axes(self):
        import matplotlib.axes

        ax = XmR(self.counts).x_plot()
        self.assertIsInstance(ax, matplotlib.axes.Axes)

    def test_x_plot_includes_expected_lines(self):
        ax = XmR(self.counts).x_plot()
        labels = self._line_labels(ax)
        for expected in ['values', 'unpl', 'cl', 'lnpl']:
            self.assertIn(expected, labels)

    def test_x_plot_marks_rule_violations(self):
        ax = XmR(self.counts).x_plot()
        # Detection-rule points are drawn as scatter collections.
        self.assertGreater(len(ax.collections), 0)

    def test_x_plot_omits_lnpl_when_below_floor(self):
        counts = [1] * 25
        counts[3] = 50
        ax = XmR(counts, limit_floor=0).x_plot()
        self.assertNotIn('lnpl', self._line_labels(ax))

    def test_x_plot_accepts_index_labels(self):
        counts = [1, 2, 3, 4]
        labels = ['a', 'b', 'c', 'd']
        ax = XmR(counts).x_plot(labels)
        self.assertEqual(len(ax.get_xticks()), len(labels))

    def test_mr_plot_returns_axes_with_expected_lines(self):
        import matplotlib.axes

        ax = XmR(self.counts).mr_plot()
        self.assertIsInstance(ax, matplotlib.axes.Axes)
        labels = self._line_labels(ax)
        for expected in ['values', 'url', 'cl']:
            self.assertIn(expected, labels)


class PlotMissingDepsTestCase(unittest.TestCase):
    def test_x_plot_raises_helpful_error_without_plot_deps(self):
        xmr = XmR([1, 2, 3])
        with mock.patch(
            'statprocon.charts.xmr.base.importlib.util.find_spec',
            return_value=None,
        ):
            with self.assertRaises(ImportError) as ctx:
                xmr.x_plot()
        self.assertIn('statprocon[plot]', str(ctx.exception))
