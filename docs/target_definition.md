# Target Definition Draft

First pass target for the project:

- Label name: risk_event_next_window
- Unit: account snapshot
- Positive label: 1 if a simulated risk event happens after the snapshot date and within the next fixed window
- Negative label: 0 otherwise

Event examples for simulation:

- missed payment
- hardship-style support flag
- collections referral

Leakage guardrail:

- Features must be built using data available on or before snapshot_date only.