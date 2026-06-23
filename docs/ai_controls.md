# AI Controls (v1)

## AI scope boundary

AI is used only for extracting structured signals from unstructured servicing notes.

AI is not used to set the final risk score directly.

## Extraction approach

Current extractor:
- deterministic keyword rules (`scripts/extract_note_signals_v1.py`)

Planned optional extension:
- LLM-based extractor as a second, bounded extractor behind schema validation

## Fallback behavior

- If note extraction fails or note rows are missing, scoring falls back to structured baseline only.
- Missing note signal defaults to `0.0` in hybrid scoring.

## Auditability controls

- Extracted signal columns are explicit and persisted.
- Extraction method is logged (`deterministic_keyword_rules_v1`).
- Hybrid score formula is explicit (`baseline_weight * baseline + note_weight * note_signal`).
- Model comparison report is generated in `reports/model_results.md`.

## Failure modes tracked in v1

- False negatives from strict keywords.
- False positives from broad words (for example generic "collections" references).
- Note tone overfitting due to synthetic templates.

## Next controls to add

- Schema-level validation for LLM extractor outputs.
- Drift checks on note-signal hit rates.
- Bias and subgroup diagnostic checks once non-synthetic data is introduced.
