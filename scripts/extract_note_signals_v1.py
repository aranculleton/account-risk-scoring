#!/usr/bin/env python3
"""Extract deterministic risk signals from servicing notes."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


KEYWORD_RULES = {
    "hardship_signal": (
        "hardship",
        "financial hardship",
        "temporary relief",
    ),
    "income_shock_signal": (
        "reduced income",
        "income reduced",
        "job loss",
        "working hours",
    ),
    "missed_payment_signal": (
        "missed payment",
        "payment missed",
        "arrears",
        "delinquency",
    ),
    "arrangement_break_signal": (
        "arrangement broke",
        "broken arrangement",
        "promise to pay broken",
    ),
    "collections_signal": (
        "collections review",
        "collections",
        "escalated",
    ),
    "vulnerability_signal": (
        "vulnerable",
        "medical",
        "mental health",
        "caregiver",
    ),
}

SIGNAL_WEIGHTS = {
    "hardship_signal": 0.20,
    "income_shock_signal": 0.20,
    "missed_payment_signal": 0.20,
    "arrangement_break_signal": 0.20,
    "collections_signal": 0.15,
    "vulnerability_signal": 0.05,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract servicing-note signals")
    parser.add_argument(
        "--notes",
        type=Path,
        default=Path("data/synthetic/servicing_notes_v1.csv"),
        help="Input servicing notes CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/synthetic/note_signals_v1.csv"),
        help="Output note signal CSV",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def extract_signals_from_text(note_text: str) -> dict[str, int]:
    text = note_text.lower()
    signals: dict[str, int] = {}
    for signal_name, keywords in KEYWORD_RULES.items():
        signals[signal_name] = int(any(keyword in text for keyword in keywords))
    return signals


def compute_note_signal_score(signals: dict[str, int]) -> float:
    score = 0.0
    for signal_name, weight in SIGNAL_WEIGHTS.items():
        score += weight * float(signals.get(signal_name, 0))
    return round(score, 4)


def parser_confidence(signals: dict[str, int]) -> float:
    positive_signals = sum(signals.values())
    if positive_signals == 0:
        return 0.68
    if positive_signals <= 2:
        return 0.86
    return 0.92


def main() -> int:
    args = parse_args()
    if not args.notes.exists():
        print(f"Input note file not found: {args.notes}")
        return 1

    rows = read_rows(args.notes)
    if not rows:
        print("Input note file is empty")
        return 1

    out_rows: list[dict[str, str]] = []
    aggregate_counts = {name: 0 for name in KEYWORD_RULES}
    skipped = 0

    for row in rows:
        text = row.get("servicing_note_text", "")
        if not text:
            skipped += 1
            continue

        signals = extract_signals_from_text(text)
        for signal_name, signal_value in signals.items():
            aggregate_counts[signal_name] += signal_value

        note_score = compute_note_signal_score(signals)
        confidence = parser_confidence(signals)

        out_row = {
            "note_id": row.get("note_id", ""),
            "snapshot_id": row.get("snapshot_id", ""),
            "account_id": row.get("account_id", ""),
            "snapshot_date": row.get("snapshot_date", ""),
            **{signal_name: str(signal_value) for signal_name, signal_value in signals.items()},
            "note_signal_score": f"{note_score:.4f}",
            "parser_confidence": f"{confidence:.2f}",
            "extraction_method": "deterministic_keyword_rules_v1",
        }
        out_rows.append(out_row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "note_id",
        "snapshot_id",
        "account_id",
        "snapshot_date",
        *KEYWORD_RULES.keys(),
        "note_signal_score",
        "parser_confidence",
        "extraction_method",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} note signal rows to {args.out}")
    print("Signal hit counts:")
    for signal_name in KEYWORD_RULES:
        print(f"- {signal_name}: {aggregate_counts[signal_name]}")
    if skipped:
        print(f"Skipped {skipped} rows with empty note text")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
