#!/usr/bin/env python3
"""Blend baseline + note signals, then compare ranking metrics."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from scoring_metrics_v1 import model_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score hybrid model and compare with baseline")
    parser.add_argument(
        "--baseline-predictions",
        type=Path,
        default=Path("data/synthetic/baseline_predictions_v1.csv"),
        help="Input baseline prediction CSV",
    )
    parser.add_argument(
        "--note-signals",
        type=Path,
        default=Path("data/synthetic/note_signals_v1.csv"),
        help="Input note signal CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/synthetic/hybrid_predictions_v1.csv"),
        help="Output hybrid prediction CSV",
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=Path("data/synthetic/model_metrics_v1.json"),
        help="Output metrics JSON",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("reports/model_results.md"),
        help="Output markdown report",
    )
    parser.add_argument("--baseline-weight", type=float, default=0.80, help="Weight for baseline score")
    parser.add_argument("--note-weight", type=float, default=0.20, help="Weight for note signal score")
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


def reviewer_proxy_text(metrics: dict[str, float | int], target_positive_share: float) -> str:
    review_share = float(metrics["reviewer_time_proxy_share"])
    review_count = int(metrics["reviewer_time_proxy_count"])
    total_rows = int(metrics["total_rows"])
    target_pct = int(round(target_positive_share * 100))
    return f"{review_share:.1%} ({review_count}/{total_rows}) for {target_pct}% escalation capture"


def write_markdown_report(
    report_path: Path,
    baseline_metrics: dict[str, float | int],
    hybrid_metrics: dict[str, float | int],
    target_positive_share: float,
) -> None:
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    content = "\n".join(
        [
            "# Model Results (v1)",
            "",
            f"Generated: {generated_utc}",
            "",
            "| Model | ROC-AUC | Precision@Top 10% | Lift@Top 10% | Reviewer-time proxy |",
            "| --- | --- | --- | --- | --- |",
            (
                "| Structured baseline | "
                f"{baseline_metrics['roc_auc']:.3f} | "
                f"{baseline_metrics['precision_top_k']:.3f} | "
                f"{baseline_metrics['lift_top_k']:.2f} | "
                f"{reviewer_proxy_text(baseline_metrics, target_positive_share)} |"
            ),
            (
                "| Structured + servicing-note signals | "
                f"{hybrid_metrics['roc_auc']:.3f} | "
                f"{hybrid_metrics['precision_top_k']:.3f} | "
                f"{hybrid_metrics['lift_top_k']:.2f} | "
                f"{reviewer_proxy_text(hybrid_metrics, target_positive_share)} |"
            ),
            "",
            "Reviewer-time proxy definition:",
            "",
            "The reviewer-time proxy estimates how many accounts a team would need to review",
            "to capture a fixed share of future escalations.",
        ]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.baseline_predictions.exists():
        print(f"Baseline predictions not found: {args.baseline_predictions}")
        return 1
    if not args.note_signals.exists():
        print(f"Note signals not found: {args.note_signals}")
        return 1

    baseline_rows = read_rows(args.baseline_predictions)
    note_rows = read_rows(args.note_signals)
    if not baseline_rows:
        print("Baseline prediction file is empty")
        return 1

    note_score_by_snapshot = {
        row["snapshot_id"]: float(row.get("note_signal_score", "0") or "0")
        for row in note_rows
        if row.get("snapshot_id")
    }

    out_rows: list[dict[str, str]] = []
    baseline_test_labels: list[int] = []
    baseline_test_scores: list[float] = []
    hybrid_test_scores: list[float] = []

    for row in baseline_rows:
        try:
            baseline_score = float(row["baseline_score"])
            label = int(row["label"])
        except (KeyError, ValueError):
            continue

        snapshot_id = row.get("snapshot_id", "")
        note_signal_score = note_score_by_snapshot.get(snapshot_id, 0.0)
        hybrid_score = args.baseline_weight * baseline_score + args.note_weight * note_signal_score
        hybrid_score = max(0.0, min(1.0, hybrid_score))

        out_rows.append(
            {
                "snapshot_id": snapshot_id,
                "account_id": row.get("account_id", ""),
                "snapshot_date": row.get("snapshot_date", ""),
                "split": row.get("split", ""),
                "label": str(label),
                "baseline_score": f"{baseline_score:.6f}",
                "note_signal_score": f"{note_signal_score:.6f}",
                "hybrid_score": f"{hybrid_score:.6f}",
            }
        )

        if row.get("split") == "test":
            baseline_test_labels.append(label)
            baseline_test_scores.append(baseline_score)
            hybrid_test_scores.append(hybrid_score)

    if not baseline_test_labels:
        print("No test rows found in baseline predictions")
        return 1

    baseline_metrics = model_metrics(
        labels=baseline_test_labels,
        scores=baseline_test_scores,
        top_fraction=args.top_fraction,
        target_positive_share=args.target_positive_share,
    )
    hybrid_metrics = model_metrics(
        labels=baseline_test_labels,
        scores=hybrid_test_scores,
        top_fraction=args.top_fraction,
        target_positive_share=args.target_positive_share,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "snapshot_id",
                "account_id",
                "snapshot_date",
                "split",
                "label",
                "baseline_score",
                "note_signal_score",
                "hybrid_score",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    metrics_payload = {
        "top_fraction": args.top_fraction,
        "target_positive_share_for_proxy": args.target_positive_share,
        "baseline": baseline_metrics,
        "hybrid": hybrid_metrics,
    }
    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    with args.metrics_out.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)

    write_markdown_report(
        report_path=args.report_out,
        baseline_metrics=baseline_metrics,
        hybrid_metrics=hybrid_metrics,
        target_positive_share=args.target_positive_share,
    )

    print(f"Wrote hybrid predictions to {args.out}")
    print(f"Wrote model metrics to {args.metrics_out}")
    print(f"Wrote markdown report to {args.report_out}")
    print(
        "Holdout comparison: "
        f"baseline ROC-AUC={baseline_metrics['roc_auc']:.4f}, "
        f"hybrid ROC-AUC={hybrid_metrics['roc_auc']:.4f}, "
        f"baseline lift@top10={baseline_metrics['lift_top_k']:.2f}, "
        f"hybrid lift@top10={hybrid_metrics['lift_top_k']:.2f}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
