import unittest

from analysis.prometheus_collect import (
    _max_sample_count,
    _mean_value,
    _max_value,
    _min_prom_samples,
    _prom_range_step,
    _sum_series_means,
    _sum_series_maxima,
    _util_pct,
)


def _series(*values: float) -> list[dict]:
    return [{"values": [[float(i), str(v)] for i, v in enumerate(values)]}]


class PrometheusCollectAggTests(unittest.TestCase):
    def test_mean_value(self) -> None:
        self.assertAlmostEqual(_mean_value(_series(10.0, 20.0, 30.0)), 20.0)

    def test_max_value(self) -> None:
        self.assertAlmostEqual(_max_value(_series(10.0, 20.0, 30.0)), 30.0)

    def test_sum_series_means_and_maxima(self) -> None:
        results = [
            {"values": [[0, "1"], [1, "3"]]},
            {"values": [[0, "2"], [1, "4"]]},
        ]
        self.assertAlmostEqual(_sum_series_means(results), 5.0)  # 2+3
        self.assertAlmostEqual(_sum_series_maxima(results), 7.0)  # 3+4

    def test_util_pct(self) -> None:
        self.assertEqual(_util_pct(0.5, 1.0), 50.0)
        self.assertEqual(_util_pct(0.0, 0.0), 0.0)

    def test_mean_lower_than_peak_for_same_series(self) -> None:
        s = _series(40.0, 80.0, 60.0)
        self.assertLess(_mean_value(s), _max_value(s))

    def test_prom_range_step_90s_window(self) -> None:
        self.assertEqual(_prom_range_step(0.0, 90.0), "5s")

    def test_min_samples_default(self) -> None:
        self.assertGreaterEqual(_min_prom_samples(), 12)

    def test_max_sample_count(self) -> None:
        self.assertEqual(_max_sample_count(_series(1.0, 2.0, 3.0, 4.0)), 4)


if __name__ == "__main__":
    unittest.main()
