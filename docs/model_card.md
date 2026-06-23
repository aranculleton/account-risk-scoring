# Model Card (v1)

## Model name

CaseSignal v1 baseline + servicing-note hybrid ranker.

## Intended use

Prioritize credit accounts for human review in a synthetic servicing workflow.

This model is decision-support only. It does not automate final credit decisions.

## Data

- Synthetic snapshot data: `data/synthetic/account_snapshot_v1.csv`
- Synthetic risk events: `data/synthetic/risk_events_v1.csv`
- Training slice: `data/synthetic/training_slice_v1.csv`
- Synthetic servicing notes: `data/synthetic/servicing_notes_v1.csv`
- Extracted note signals: `data/synthetic/note_signals_v1.csv`

## Label

`risk_event_next_window` from event occurrence in the next 90 days.

## Feature groups

Structured baseline:
- utilization
- payments due
- recent missed-payment/hardship/collections flags
- derived distress indicators
- months-on-book scaling

Servicing-note signals:
- hardship signal
- income shock signal
- missed-payment signal
- arrangement-break signal
- collections signal
- vulnerability signal

## Evaluation protocol

- Time-ordered holdout split from training slice.
- Ranking metrics: ROC-AUC, precision@top 10%, lift@top 10%.
- Reviewer-time proxy at fixed escalation capture target.
- Current results: `reports/model_results.md`.

## Key limitations

- Synthetic data only; real-world transfer is unknown.
- Notes are template-generated, not naturally written servicing logs.
- Deterministic extractor may miss paraphrases and context nuance.
- No fairness testing on protected attributes in this v1 slice.
- No production calibration monitoring in this repository.

## Human-in-the-loop policy

- Scores and note signals support analyst triage.
- Final actions remain reviewer-owned.
- If note extraction fails, fallback is structured-only ranking.
