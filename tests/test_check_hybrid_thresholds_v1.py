from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_hybrid_thresholds_v1.py"
SPEC = importlib.util.spec_from_file_location("check_hybrid_thresholds_v1", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ThresholdHelperTests(unittest.TestCase):
    def test_quantile_clamps_bounds(self) -> None:
        values = [0.10, 0.20, 0.30]
        self.assertAlmostEqual(MODULE.quantile(values, -1.0), 0.10)
        self.assertAlmostEqual(MODULE.quantile(values, 2.0), 0.30)

    def test_quantile_midpoint_selection(self) -> None:
        values = [0.10, 0.20, 0.30, 0.40, 0.50]
        self.assertAlmostEqual(MODULE.quantile(values, 0.50), 0.30)

    def test_collect_scores_filters_split_and_skips_bad_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "hybrid_predictions.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["split", "hybrid_score"])
                writer.writeheader()
                writer.writerows(
                    [
                        {"split": "train", "hybrid_score": "0.42"},
                        {"split": "test", "hybrid_score": "0.20"},
                        {"split": "test", "hybrid_score": "0.10"},
                        {"split": "test", "hybrid_score": "not-a-number"},
                    ]
                )

            self.assertEqual(MODULE.collect_scores(csv_path, "test"), [0.10, 0.20])
            self.assertEqual(MODULE.collect_scores(csv_path, "all"), [0.10, 0.20, 0.42])


if __name__ == "__main__":
    unittest.main()
