# Account Risk Scoring

This repo is a small sandbox for building an account risk watchlist from monthly snapshots.

The current approach is simple on purpose: generate synthetic account data, define a first feature slice in SQL, and test scoring ideas before introducing a full model pipeline.

## What is here now

- synthetic snapshot generator: `scripts/generate_account_snapshots_v1.py`
- snapshot schema draft: `docs/account_snapshot_schema_v1.md`
- target definition draft: `docs/target_definition.md`
- first feature SQL draft: `sql/account_month_features_v1.sql`

## Quick start

Generate synthetic snapshot data:

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
```

This writes `data/synthetic/account_snapshot_v1.csv` (gitignored).

## Optional JAX first step

If you want to start using JAX early, install the CPU package and run the smoke script:

```bash
pip install "jax[cpu]"
python3 scripts/jax_score_smoke.py --input data/synthetic/account_snapshot_v1.csv --top-n 10
```

The script reads the snapshot CSV and prints the top rows by a basic JAX-based risk score. It is not a trained model yet, just a first vectorized scoring pass.

## Next likely steps

- add a small synthetic event table for label generation
- run the SQL feature draft in a repeatable local query flow
- replace heuristic weights with a fitted baseline model
