#!/usr/bin/env python3
"""Train a thin baseline credit-risk model and export predictions/metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path

from scoring_metrics_v1 import model_metrics


FEATURE_NAMES = [
    "utilization_ratio",
    "payments_due_30d_scaled",
    "missed_payment_90d",
    "hardship_flag_90d",
    "collections_contact_90d",
    "high_utilization_flag",
    "any_recent_distress_flag",
    "months_on_book_scaled",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline model on training_slice_v1.csv")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/synthetic/training_slice_v1.csv"),
        help="Feature + label CSV",
    )
    parser.add_argument(
        "--predictions-out",
        type=Path,
        default=Path("data/synthetic/baseline_predictions_v1.csv"),
        help="Output prediction CSV",
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=Path("data/synthetic/model_metrics_v1.json"),
        help="Metrics JSON output",
    )
    parser.add_argument("--test-ratio", type=float, default=0.20, help="Holdout ratio based on snapshot_date order")
    parser.add_argument("--epochs", type=int, default=1500, help="Gradient-descent epochs")
    parser.add_argument("--learning-rate", type=float, default=0.20, help="Gradient-descent learning rate")
    parser.add_argument("--l2", type=float, default=0.002, help="L2 regularization strength")
    parser.add_argument("--top-fraction", type=float, default=0.10, help="Top-k fraction for precision/lift")
    parser.add_argument(
        "--target-positive-share",
        type=float,
        default=0.50,
        help="Target share of positives for reviewer-time proxy",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def to_feature_vector(row: dict[str, str]) -> list[float]:
    return [
        float(row["utilization_ratio"]),
        float(row["payments_due_30d"]) / 3.0,
        float(row["missed_payment_90d"]),
        float(row["hardship_flag_90d"]),
        float(row["collections_contact_90d"]),
        float(row["high_utilization_flag"]),
        float(row["any_recent_distress_flag"]),
        float(row["months_on_book"]) / 120.0,
    ]


def sigmoid(value: float) -> float:
    if value >= 0:
        exp_term = math.exp(-value)
        return 1.0 / (1.0 + exp_term)
    exp_term = math.exp(value)
    return exp_term / (1.0 + exp_term)


def dot_product(lhs: list[float], rhs: list[float]) -> float:
    return sum(a * b for a, b in zip(lhs, rhs))


def fit_logistic_regression(
    x_values: list[list[float]],
    y_values: list[int],
    epochs: int,
    learning_rate: float,
    l2: float,
) -> tuple[list[float], float]:
    if not x_values:
        raise ValueError("No training rows provided")

    weights = [0.0] * len(x_values[0])
    bias = 0.0

    for _ in range(epochs):
        grad_w = [0.0] * len(weights)
        grad_b = 0.0

        for features, label in zip(x_values, y_values):
            probability = sigmoid(dot_product(weights, features) + bias)
            error = probability - label
            grad_b += error
            for idx, feature in enumerate(features):
                grad_w[idx] += error * feature

        sample_count = float(len(x_values))
        grad_b /= sample_count
        for idx in range(len(weights)):
            grad_w[idx] = grad_w[idx] / sample_count + l2 * weights[idx]
            weights[idx] -= learning_rate * grad_w[idx]

        bias -= learning_rate * grad_b

    return weights, bias


def predict_scores(x_values: list[list[float]], weights: list[float], bias: float) -> list[float]:
    return [sigmoid(dot_product(weights, features) + bias) for features in x_values]


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"Input file not found: {args.input}")
        return 1

    rows = read_rows(args.input)
    if len(rows) < 50:
        print("Need at least 50 rows to train and evaluate baseline model")
        return 1

    parsed_rows: list[dict[str, str | int | date | list[float]]] = []
    skipped = 0
    for row in rows:
        try:
            snapshot_date = date.fromisoformat(row["snapshot_date"])
            label = int(row["risk_event_next_window"])
            features = to_feature_vector(row)
        except (KeyError, ValueError):
            skipped += 1
            continue

        parsed_rows.append(
            {
                "snapshot_id": row["snapshot_id"],
                "account_id": row["account_id"],
                "snapshot_date": snapshot_date,
                "label": label,
                "features": features,
            }
        )

    parsed_rows.sort(key=lambda item: item["snapshot_date"])
    if len(parsed_rows) < 50:
        print("Not enough valid rows after parsing")
        return 1

    split_idx = int(len(parsed_rows) * (1.0 - args.test_ratio))
    split_idx = max(1, min(split_idx, len(parsed_rows) - 1))

    train_rows = parsed_rows[:split_idx]
    test_rows = parsed_rows[split_idx:]

    x_train = [row["features"] for row in train_rows]
    y_train = [int(row["label"]) for row in train_rows]

    weights, bias = fit_logistic_regression(
        x_values=x_train,
        y_values=y_train,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        l2=args.l2,
    )

    x_all = [row["features"] for row in parsed_rows]
    all_scores = predict_scores(x_all, weights, bias)

    prediction_rows: list[dict[str, str]] = []
    for idx, row in enumerate(parsed_rows):
        split = "train" if idx < split_idx else "test"
        prediction_rows.append(
            {
                "snapshot_id": str(row["snapshot_id"]),
                "account_id": str(row["account_id"]),
                "snapshot_date": str(row["snapshot_date"]),
                "split": split,
                "label": str(int(row["label"])),
                "baseline_score": f"{all_scores[idx]:.6f}",
            }
        )

    args.predictions_out.parent.mkdir(parents=True, exist_ok=True)
    with args.predictions_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "snapshot_id",
                "account_id",
                "snapshot_date",
                "split",
                "label",
                "baseline_score",
            ],
        )
        writer.writeheader()
        writer.writerows(prediction_rows)

    test_labels = [int(row["label"]) for row in test_rows]
    test_scores = all_scores[split_idx:]
    test_metrics = model_metrics(
        labels=test_labels,
        scores=test_scores,
        top_fraction=args.top_fraction,
        target_positive_share=args.target_positive_share,
    )

    metrics_payload = {
        "model": "structured_baseline_logistic_v1",
        "features": FEATURE_NAMES,
        "evaluation_split": "time_holdout",
        "top_fraction": args.top_fraction,
        "target_positive_share_for_proxy": args.target_positive_share,
        "baseline": test_metrics,
    }

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    with args.metrics_out.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)

    print(f"Trained baseline model on {len(train_rows)} rows; holdout rows: {len(test_rows)}")
    print(f"Wrote predictions to {args.predictions_out}")
    print(f"Wrote metrics to {args.metrics_out}")
    if skipped:
        print(f"Skipped {skipped} malformed rows while parsing inputs")

    print(
        "Holdout metrics: "
        f"ROC-AUC={test_metrics['roc_auc']:.4f}, "
        f"Precision@Top10%={test_metrics['precision_top_k']:.4f}, "
        f"Lift@Top10%={test_metrics['lift_top_k']:.2f}, "
        f"ReviewerTimeProxy={test_metrics['reviewer_time_proxy_share']:.2%}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
