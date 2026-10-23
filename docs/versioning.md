# Versions

[Back to the README](../README.md) · [plan](prepay_plan.md) · [seed pools](seeds.md) · [decision log](decision_log.md)

One row per released or frozen version. A version is never edited once used; a change is a new row.

| Release | Data | Score | Workflow | Agent | Status |
|---|---|---|---|---|---|
| P1 | 4.2 (generator pinned in `GENERATOR_PIN`) | P1.0 ([spec](score_prepay.md)) | WP1.0 (superseded: final run missed, [result](wp10_final_dev.md)); **WP1.1** ([freeze](wp11_freeze.md), final development run passed, [result](wp11_final_dev.md)) | AP1.0 (issue 6, paid, built and parity-checked, not run) | WP1.1 frozen; fresh test seeds unread |

Reference arms (not versions): pay-all, claim edits, automatic adjustment, the oracle with triage ([results](prepay_reference_arms.md)).

Seed pools and who used which seeds: [seeds.md](seeds.md), generated from `experiments/seed_registry.json`.
