# Decision log

| Date | Event | Detail |
|---|---|---|
| 2026-10-23 | Repository created | From em-upcoding-agent; prepay point 4; see LINEAGE.md. |
| 2026-10-23 | Seed plan for the P-DEV pool declared (issue 4) | Reference tuning: select j = 10 to 19 (j = 0 to 9 already read with first guesses), tuned arms read once on j = 20 to 29. WP1.0: fit j = 30 to 39, select j = 40 to 49, final development run j = 50 to 59. P-CONFIRM, P-TEST, P-RESERVED untouched. |
| 2026-10-23 | Reference arms tuned on P-DEV (issue 5 setup) | Select j = 10 to 19 (126 settings), hold-out read once on j = 20 to 29. Claim edits tuned: +$203,877 on the hold-out (planted impossible-day claims, see docs/prepay_reference_arms.md). Provider-level adjustment: no setting beats pay-all, tuned arm = pay-all. Stream gained `rendering` and `has_test`. No fresh pool touched. |
