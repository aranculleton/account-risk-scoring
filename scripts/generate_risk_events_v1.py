#!/usr/bin/env python3
"""Generate synthetic risk events from account snapshot rows."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic risk events")
    parser.add_argument("--snapshots", type=Path, default=Path("data/synthetic/account_snapshot_v1.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/synthetic/risk_events_v1.csv"))
    parser.add_argument("--seed", type=int, default=21)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def choose_event_type(rng: random.Random, missed: int, hardship: int, collections: int) -> str:
    if collections:
        return rng.choice(["collections_referral", "missed_payment"])
    if hardship:
        return rng.choice(["hardship_support", "missed_payment"])
    if missed:
        return rng.choice(["missed_payment", "collections_referral"])
    return rng.choice(["missed_payment", "hardship_support", "collections_referral"])


def main() -> int:
    args = parse_args()
    if not args.snapshots.exists():
        print(f"Snapshot file not found: {args.snapshots}")
        return 1

    rng = random.Random(args.seed)
    snapshot_rows = read_rows(args.snapshots)
    events: list[dict[str, str]] = []

    for row in snapshot_rows:
        try:
            snapshot_date = date.fromisoformat(row["snapshot_date"])
            util = float(row["utilization_ratio"])
            missed = int(row["missed_payment_90d"])
            hardship = int(row["hardship_flag_90d"])
            collections = int(row["collections_contact_90d"])
        except (KeyError, ValueError):
            continue

        high_util = 1 if util >= 0.90 else 0
        p_event = 0.02 + 0.20 * missed + 0.14 * hardship + 0.18 * collections + 0.08 * high_util
        if rng.random() >= min(p_event, 0.95):
            continue

        event_date = snapshot_date + timedelta(days=rng.randint(1, 90))
        events.append(
            {
                "event_id": f"E{len(events) + 1:07d}",
                "account_id": row["account_id"],
                "snapshot_date": snapshot_date.isoformat(),
                "event_date": event_date.isoformat(),
                "event_type": choose_event_type(rng, missed, hardship, collections),
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["event_id", "account_id", "snapshot_date", "event_date", "event_type"]
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

    print(f"Wrote {len(events)} events from {len(snapshot_rows)} snapshot rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())