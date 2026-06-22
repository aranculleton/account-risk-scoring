# Risk Event Schema v1

This table is the first synthetic event source for label generation.

Table name: `risk_events_v1`

Grain: one row per risk event for an account.

Columns:

| column | type | note |
| --- | --- | --- |
| event_id | text | event row id |
| account_id | text | account id from snapshot data |
| snapshot_date | date | snapshot row date that the event was generated from |
| event_date | date | event date in the 1 to 90 day window after snapshot_date |
| event_type | text | one of `missed_payment`, `hardship_support`, `collections_referral` |

Current scope limits:
- synthetic only
- no event severity value yet
- no separate source table per event type yet