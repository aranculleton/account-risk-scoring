# CaseSignal

`casesignal` is a practical account-risk scoring project.

## What is account-risk scoring?

Account-risk scoring means ranking accounts by the chance of a near-term credit-risk outcome,
such as missed payments, arrears escalation, or collections handoff, so teams can intervene earlier.

CaseSignal is a prototype decision-support pipeline for that workflow.

Given monthly account data and case history text, the target output is:
- a risk score
- reason signals that explain why risk moved
- a short triage summary with suggested next action

All data in this repository is synthetic.

## Why use AI here?

Structured models are useful, but they often miss high-signal context buried in servicing notes.

AI is used for one bounded job: converting free-text case notes into a small, auditable set of structured indicators
(for example hardship mention, income shock language, or vulnerability context).

In this project, "case notes" means operational notes captured during account servicing,
for example payment-arrangement discussions, hardship reviews, and follow-up calls.

The final score remains deterministic and reviewable:
- baseline structured model score
- note-signal feature block
- transparent score combination and action bands

If note extraction fails, the pipeline falls back to structured-only scoring.

## Current status

Already in place:
- synthetic snapshots and events generation
- SQL feature and label drafts
- training slice export

Core files:
- `scripts/generate_account_snapshots_v1.py`
- `scripts/generate_risk_events_v1.py`
- `scripts/export_training_slice_v1.py`
- `sql/account_month_features_v1.sql`
- `sql/labels_from_events_v1.sql`

## Two-week MVP scope

Week 1:
1. train a baseline model on `training_slice_v1.csv`
2. generate synthetic case notes linked to account-month rows
3. define note-signal schema + deterministic fallback parser

Week 2:
1. add note-signal extraction step
2. build hybrid score + action banding
3. compare baseline vs hybrid (`precision@top-k`, lift, reviewer-time proxy)

This scope is intentionally sized for one developer over two focused weeks.

## Quick run (current data flow)

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
python3 scripts/generate_risk_events_v1.py
python3 scripts/export_training_slice_v1.py
```

Expected outputs:
- `data/synthetic/account_snapshot_v1.csv`
- `data/synthetic/risk_events_v1.csv`
- `data/synthetic/training_slice_v1.csv`

## Roadmap

Detailed build plan: `docs/ai_workflow_roadmap.md`.
