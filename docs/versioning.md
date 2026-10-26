# Versions

[Back to the README](../README.md) · [plan](prepay_plan.md) · [seed pools](seeds.md) · [decision log](decision_log.md)

One row per released or frozen version. A version is never edited once used; a change is a new row.

| Release | Data | Score | Workflow | Agent | Status |
|---|---|---|---|---|---|
| P1 | 4.2 (generator pinned in `GENERATOR_PIN`) | P1.0 ([spec](score_prepay.md)) | WP1.0 (superseded, [final run missed](wp10_final_dev.md)); **WP1.1** ([freeze](wp11_freeze.md), [true test passed](p1_test.md)) | AP1.0 ([design](ap10.md); true test: worse than WP1.1, [result](p1_test.md)) | tested 2026-10-25; P-TEST j = 0 to 9 burned |

Reference arms (not versions): pay-all, claim edits, automatic adjustment, the oracle with triage ([results](prepay_reference_arms.md)).

Seed pools and who used which seeds: [seeds.md](seeds.md), generated from `experiments/seed_registry.json`.
