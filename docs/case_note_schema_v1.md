# Servicing Note Schema (v1)

This document defines the account-month servicing note contract used in CaseSignal v1.

## Input note row

File: `data/synthetic/servicing_notes_v1.csv`

Columns:
- `note_id`
- `snapshot_id`
- `account_id`
- `snapshot_date`
- `servicing_note_text`
- `note_tone`

## Extracted signal row

File: `data/synthetic/note_signals_v1.csv`

Columns:
- `note_id`
- `snapshot_id`
- `account_id`
- `snapshot_date`
- `hardship_signal` (0/1)
- `income_shock_signal` (0/1)
- `missed_payment_signal` (0/1)
- `arrangement_break_signal` (0/1)
- `collections_signal` (0/1)
- `vulnerability_signal` (0/1)
- `note_signal_score` (0.0-1.0 weighted score)
- `parser_confidence` (0.0-1.0 confidence proxy)
- `extraction_method` (string)

## Deterministic extraction method

Script: `scripts/extract_note_signals_v1.py`

Method:
- lower-case text
- keyword pattern checks per signal
- weighted score from fixed signal weights
- confidence proxy from number of triggered signals

## Governance notes

- v1 is deterministic and auditable.
- if no note is present, hybrid scoring defaults note contribution to zero.
- this schema is intentionally small for thin-MVP traceability.
