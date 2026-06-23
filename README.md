# Account Risk Scoring

This repo is a practical account-risk pipeline built in small, realistic steps.

In plain terms, it does this:
- generate synthetic account snapshots
- generate synthetic risk events
- build features and labels
- export a training slice for modeling

All data is synthetic at this stage.

Key files:
- `scripts/generate_account_snapshots_v1.py`
- `scripts/generate_risk_events_v1.py`
- `scripts/export_training_slice_v1.py`
- `sql/account_month_features_v1.sql`
- `sql/labels_from_events_v1.sql`
- `docs/account_snapshot_schema_v1.md`
- `docs/target_definition.md`
- `docs/ai_workflow_roadmap.md`

Why the AI workflow matters here:
- many roles now ask for evidence of using Claude/Codex in real delivery work
- this repo is set up to show that in a measurable way
- goal is not "AI wrote code"; goal is faster iteration with human checks

How AI is being used:
- AI helps draft feature/SQL/model changes
- each change is reviewed and either accepted or rejected
- we keep checks around leakage, shape, and reproducibility

Generate snapshots:

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
```

Output: `data/synthetic/account_snapshot_v1.csv` (gitignored).

Generate events and training slice:

```bash
python3 scripts/generate_risk_events_v1.py
python3 scripts/export_training_slice_v1.py
```

JAX step (optional):

JAX is currently used for a quick vectorized score check only.
Baseline model training is a separate next step.

Install and run:

```bash
pip install "jax[cpu]"
python3 scripts/jax_score_smoke.py --input data/synthetic/account_snapshot_v1.csv --top-n 10
```

What this script does:
- reads the snapshot CSV
- builds a feature matrix from existing columns
- applies fixed weights and prints highest-score rows

Next steps:

- add first baseline model script using `training_slice_v1.csv`
- add AI review logs for accepted/rejected suggestions
- keep refining label quality and event generation assumptions
