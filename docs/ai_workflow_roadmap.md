# AI Workflow Roadmap (Plan Only)

This is a practical plan to integrate AI tooling into the project in a way that is useful for real work and credible on a CV.

## Brutally honest view

- Using Claude/Codex by itself is not strong CV evidence.
- Employers care more about: what changed in delivery speed/quality, how safe/reproducible the workflow is, and whether you can verify AI outputs.
- Best move is to keep this project and add an AI-assisted engineering layer around it.
- Full migration to an "AI project" is not needed right now and could weaken the risk-scoring narrative.

## Target outcome

By the end, the project should show:
- reproducible baseline model pipeline
- AI-assisted feature/model workflow with human review checkpoints
- measurable deltas (time saved, defects caught, experiments completed)
- clear documentation of where AI was used and where it was rejected

## Why this is worth doing

This is designed to be useful for hiring conversations:
- proves AI was integrated into delivery, not just experimented with
- shows human review and quality gates around AI suggestions
- links each workflow change to concrete output (metrics, logs, run artifacts)

## Execution style

- one thin slice per session
- one main concern per commit
- keep human review explicit
- push in small increments

## Phase plan

## Phase 1: Baseline model (non-AI control)

Goal:
- establish a normal baseline workflow before AI integration

Deliverables:
- baseline model script using `training_slice_v1.csv`
- basic metrics output (ROC-AUC, PR-AUC, label rate)
- small run log artifact

Commit pattern:
1. add `scripts/train_baseline_v1.py`
2. add metric output file path + README note
3. tidy script args and defaults after first run

CV evidence:
- "Built baseline account-risk model pipeline from synthetic snapshots/events to labeled training slice and metrics output."

## Phase 2: AI-assisted feature proposal loop

Goal:
- use AI to propose feature changes, but gate with human review

Deliverables:
- `prompts/feature_ideas_v1.md` (prompt templates)
- `docs/feature_review_log.md` (accept/reject with reason)
- first accepted feature change + one rejected suggestion

Commit pattern:
1. add prompt and review-log templates
2. add one accepted feature change
3. add one rejected AI suggestion entry

CV evidence:
- "Ran AI-assisted feature ideation with explicit review logging; accepted and rejected suggestions based on leakage and signal checks."

## Phase 3: AI-assisted SQL iteration with checks

Goal:
- use AI for SQL drafts while enforcing deterministic checks

Deliverables:
- SQL checklist (`docs/sql_review_checklist.md`)
- one AI-drafted SQL revision with manual corrections recorded
- simple query-validation script or smoke query runner

Commit pattern:
1. add SQL checklist
2. apply one SQL revision from AI draft
3. add/adjust validation check

CV evidence:
- "Integrated AI SQL drafting with manual validation checklist to prevent schema drift and leakage."

## Phase 4: Experiment ledger and reproducibility

Goal:
- make AI-assisted and manual experiments traceable

Deliverables:
- `experiments/ledger.csv` (run_id, change, ai_used, outcome)
- `scripts/run_experiment_v1.py` or similar helper
- stable run naming convention

Commit pattern:
1. add ledger format
2. add run helper script
3. log first 2-3 experiments

CV evidence:
- "Added experiment ledger linking code changes to outcomes across AI-assisted and manual runs."

## Phase 5: Quality gates for AI usage

Goal:
- prove outputs are checked, not blindly accepted

Deliverables:
- lightweight policy doc (`docs/ai_usage_policy.md`)
- pre-push checks for key scripts/SQL
- explicit checklist item: leakage, label window, data-shape sanity

Commit pattern:
1. add policy + checklist
2. add pre-push command docs/task
3. update after first real failure caught

CV evidence:
- "Introduced AI usage guardrails and pre-push checks; caught and fixed quality issues before merge."

## Phase 6: Portfolio/CV packaging

Goal:
- present this as an engineering workflow case study, not "I used AI"

Deliverables:
- short case-study doc (`docs/case_study_ai_workflow.md`)
- quantified outcomes section (speed, quality, confidence)
- concise CV bullets tied to artifacts

Commit pattern:
1. case-study draft
2. add quantified results from ledger
3. tighten wording and links

CV evidence:
- "Built a human-reviewed AI-assisted risk modeling workflow with reproducible experiment tracking and quality gates."

## What not to do

- do not claim autonomous AI model-building
- do not skip baseline/non-AI control
- do not merge AI suggestions without traceable review notes
- do not flood commits with unrelated refactors

## Next immediate step

- implement Phase 1, commit 1:
  - add `scripts/train_baseline_v1.py`
  - keep it simple (logistic baseline + metrics)
