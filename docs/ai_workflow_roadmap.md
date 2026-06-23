# CaseSignal Roadmap (2-Week MVP)

Goal:
build and evaluate a practical credit-risk decisioning pipeline that combines
structured credit-account behavior with AI-extracted servicing-note signals.

## Status snapshot (current)

Completed:
- structured baseline training and holdout scoring
- synthetic servicing-note generation
- deterministic note-signal extraction
- baseline vs hybrid evaluation report
- model card and AI controls notes

Remaining:
- triage summary/action output script (`scripts/generate_case_summary_v1.py`)
- optional LLM extractor as a bounded extension behind schema validation

## Problem

Credit-risk decisioning ranks accounts by likelihood of near-term adverse outcomes,
for example missed payments, delinquency progression, or arrears escalation.

Structured features usually capture payment and account behavior well,
but they can miss early warnings that appear first in servicing notes.

## Solution shape

1. Structured baseline model
- snapshots -> features -> labels -> baseline score

2. Note signal layer
- synthetic servicing notes -> AI extraction -> structured note indicators

3. Hybrid score
- combine baseline score and note indicators

4. Triage output
- risk band + short reason summary + suggested review action

## Why AI is a good fit here

- The hard part is unstructured text, which is exactly where AI helps.
- The model output remains bounded and auditable.
- The pipeline can run with deterministic fallback when AI extraction is unavailable.
- The output is operationally useful: rank + reason + action, not just a probability.

## MVP guardrails

- synthetic data only
- no autonomous decisioning
- small extraction schema (5-10 note indicators)
- deterministic fallback parser
- explicit confidence thresholds on extracted signals
- leakage checks remain mandatory

## Week 1 plan

1. Baseline model
- `scripts/train_baseline_model_v1.py`
- output ROC-AUC, PR-AUC, calibration note
- save row-level predictions for comparison

2. Synthetic servicing-note dataset
- `scripts/generate_servicing_notes_v1.py`
- link servicing notes to account-month grain
- document schema in `docs/case_note_schema_v1.md`

3. Note-signal contract
- define extraction JSON schema
- implement deterministic fallback parser

## Week 2 plan

1. Note extraction step
- `scripts/extract_note_signals_v1.py`
- persist indicators + confidence scores

2. Hybrid score assembly
- `scripts/score_hybrid_model_v1.py`
- combine structured and note signal components

3. Triage summary output
- `scripts/generate_case_summary_v1.py`
- output reason/action packs for review queues

4. Evaluation
- compare baseline vs hybrid
- report `precision@top-k`, lift, and reviewer-time proxy
- add short model-card style limitations and governance notes

## Immediate next step

Implement baseline training first (`train_baseline_model_v1.py`) and lock baseline metrics.
Then add note-signal AI as an incremental layer.

Immediate artifact targets:
- `reports/model_results.md`
- `docs/model_card.md`
- `docs/ai_controls.md`
