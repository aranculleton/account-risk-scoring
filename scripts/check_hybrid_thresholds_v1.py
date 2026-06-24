#!/usr/bin/env python3
"""Inspect hybrid score distribution and suggest band thresholds."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check hybrid-score distribution")
    parser.add_argument(
        "--hybrid-predictions",
        type=Path,
        default=Path("data/synthetic/hybrid_predictions_v1.csv"),
        help="Hybrid predictions CSV",
    )
    parser.add_argument(
        "--split",
        choices=("all", "train", "test"),
        default="test",
        help="Which split to evaluate",
    )
    parser.add_argument("--high-quantile", type=float, default=0.95, help="Quantile for high-risk threshold")
    parser.add_argument(
        "--elevated-quantile",
        type=float,
        default=0.85,
        help="Quantile for elevated-risk threshold",
    )
    return parser.parse_args()


def quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    q = max(0.0, min(1.0, q))
    idx = int(round((len(sorted_values) - 1) * q))
    return sorted_values[idx]


def collect_scores(predictions_path: Path, split: str) -> list[float]:
    scores: list[float] = []
    with predictions_path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if split != "all" and row.get("split") != split:
                continue
            try:
                scores.append(float(row["hybrid_score"]))
            except (KeyError, ValueError):
                continue
    scores.sort()
    return scores


def main() -> int:
    args = parse_args()
    if not args.hybrid_predictions.exists():
        print(f"Missing input: {args.hybrid_predictions}")
        return 1
    if args.elevated_quantile > args.high_quantile:
        print("elevated-quantile must be <= high-quantile")
        return 1

    scores = collect_scores(args.hybrid_predictions, args.split)

    if not scores:
        print("No scores found for requested split")
        return 1

    print(f"Rows evaluated: {len(scores)} (split={args.split})")
    for q in (0.50, 0.75, 0.90, 0.95, 0.99):
        print(f"p{int(q * 100):02d}: {quantile(scores, q):.4f}")

    elevated_threshold = quantile(scores, args.elevated_quantile)
    high_threshold = quantile(scores, args.high_quantile)
    print("Suggested thresholds:")
    print(f"- elevated ({args.elevated_quantile:.0%}): {elevated_threshold:.4f}")
    print(f"- high ({args.high_quantile:.0%}): {high_threshold:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
