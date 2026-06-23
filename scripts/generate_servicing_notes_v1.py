#!/usr/bin/env python3
"""Generate synthetic servicing notes linked to account-month snapshots."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic servicing notes")
    parser.add_argument(
        "--training-slice",
        type=Path,
        default=Path("data/synthetic/training_slice_v1.csv"),
        help="Input training slice CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/synthetic/servicing_notes_v1.csv"),
        help="Output servicing note CSV",
    )
    parser.add_argument("--seed", type=int, default=77, help="Random seed")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def build_servicing_note(row: dict[str, str], rng: random.Random) -> tuple[str, str]:
    missed = int(row["missed_payment_90d"])
    hardship = int(row["hardship_flag_90d"])
    collections = int(row["collections_contact_90d"])
    utilization = float(row["utilization_ratio"])
    payments_due = int(row["payments_due_30d"])

    clauses: list[str] = []
    tone = "low_risk"

    if missed:
        clauses.append("Customer confirmed a missed payment this cycle.")
        tone = "elevated_risk"

    if hardship:
        hardship_options = [
            "Customer reported financial hardship after reduced income.",
            "Customer requested hardship support due to reduced working hours.",
        ]
        clauses.append(rng.choice(hardship_options))
        tone = "elevated_risk"

    if collections:
        clauses.append("Previous payment arrangement broke; collections review was requested.")
        tone = "high_risk"

    if utilization >= 0.90:
        clauses.append("Credit utilization remains elevated against the current limit.")
        if tone == "low_risk":
            tone = "elevated_risk"

    if payments_due >= 2:
        clauses.append("Multiple payments are currently due.")
        if tone == "low_risk":
            tone = "elevated_risk"

    if not clauses:
        healthy_options = [
            "Customer confirmed stable income and regular payment behavior.",
            "No hardship indicators were discussed during servicing contact.",
            "Account activity appears stable with no missed payment signal in conversation.",
        ]
        clauses.append(rng.choice(healthy_options))

    follow_up = rng.choice(
        [
            "Follow-up scheduled within 7 days.",
            "Next review date set for the upcoming billing cycle.",
            "Servicing team to monitor account in routine queue.",
        ]
    )
    clauses.append(follow_up)

    return " ".join(clauses), tone


def main() -> int:
    args = parse_args()
    if not args.training_slice.exists():
        print(f"Training slice not found: {args.training_slice}")
        return 1

    rows = read_rows(args.training_slice)
    if not rows:
        print("Training slice is empty")
        return 1

    rng = random.Random(args.seed)
    note_rows: list[dict[str, str]] = []
    tone_counts = {"low_risk": 0, "elevated_risk": 0, "high_risk": 0}
    skipped = 0

    for idx, row in enumerate(rows, start=1):
        try:
            note_text, tone = build_servicing_note(row, rng)
        except (KeyError, ValueError):
            skipped += 1
            continue

        tone_counts[tone] = tone_counts.get(tone, 0) + 1
        note_rows.append(
            {
                "note_id": f"N{idx:07d}",
                "snapshot_id": row["snapshot_id"],
                "account_id": row["account_id"],
                "snapshot_date": row["snapshot_date"],
                "servicing_note_text": note_text,
                "note_tone": tone,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "note_id",
                "snapshot_id",
                "account_id",
                "snapshot_date",
                "servicing_note_text",
                "note_tone",
            ],
        )
        writer.writeheader()
        writer.writerows(note_rows)

    print(f"Wrote {len(note_rows)} servicing notes to {args.out}")
    print("Tone distribution:")
    for tone in ("low_risk", "elevated_risk", "high_risk"):
        print(f"- {tone}: {tone_counts.get(tone, 0)}")
    if skipped:
        print(f"Skipped {skipped} rows due to missing fields")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
