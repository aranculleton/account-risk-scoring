-- Draft account-month feature query (v1).
-- Assumes `account_snapshot_v1` has already been loaded into a local DB.
-- Temporary: no label join yet, just first-pass feature columns.

WITH base AS (
    SELECT
        snapshot_id,
        account_id,
        CAST(snapshot_date AS DATE) AS snapshot_date,
        months_on_book,
        credit_limit,
        balance,
        utilization_ratio,
        payments_due_30d,
        missed_payment_90d,
        hardship_flag_90d,
        collections_contact_90d
    FROM account_snapshot_v1
),
features AS (
    SELECT
        snapshot_id,
        account_id,
        snapshot_date,
        months_on_book,
        credit_limit,
        balance,
        utilization_ratio,
        payments_due_30d,
        missed_payment_90d,
        hardship_flag_90d,
        collections_contact_90d,
        CASE WHEN utilization_ratio >= 0.90 THEN 1 ELSE 0 END AS high_utilization_flag,
        CASE
            WHEN (missed_payment_90d + hardship_flag_90d + collections_contact_90d) > 0 THEN 1
            ELSE 0
        END AS any_recent_distress_flag
    FROM base
)
SELECT
    snapshot_id,
    account_id,
    snapshot_date,
    months_on_book,
    credit_limit,
    balance,
    utilization_ratio,
    payments_due_30d,
    missed_payment_90d,
    hardship_flag_90d,
    collections_contact_90d,
    high_utilization_flag,
    any_recent_distress_flag
FROM features;