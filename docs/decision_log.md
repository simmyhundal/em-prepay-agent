# Decision log

| Date | Event | Detail |
|---|---|---|
| 2026-10-23 | Repository created | From em-upcoding-agent; prepay point 4; see LINEAGE.md. |
| 2026-10-23 | Seed plan for the P-DEV pool declared (issue 4) | Reference tuning: select j = 10 to 19 (j = 0 to 9 already read with first guesses), tuned arms read once on j = 20 to 29. WP1.0: fit j = 30 to 39, select j = 40 to 49, final development run j = 50 to 59. P-CONFIRM, P-TEST, P-RESERVED untouched. |
| 2026-10-23 | Reference arms tuned on P-DEV (issue 5 setup) | Select j = 10 to 19 (126 settings), hold-out read once on j = 20 to 29. Claim edits tuned: +$203,877 on the hold-out (planted impossible-day claims, see docs/prepay_reference_arms.md). Provider-level adjustment: no setting beats pay-all, tuned arm = pay-all. Stream gained `rendering` and `has_test`. No fresh pool touched. |
| 2026-10-23 | WP1.0 hypothesis loop on P-DEV select j = 40 to 49 (issue 5) | 10 changes, about 59 further settings. Candidate H7 (train on resolved pends only): $187,644 over 10 seeds vs tuned edit $172,511 (p = 0.47). See docs/wp10_loop.md. |
| 2026-10-23 | P-CONFIRM flipped fresh to in_use; WP1.0 confirm declared (j = 0 to 19) | docs/wp10_confirm_declaration.md, committed before any confirm seed is built. P-CONFIRM j = 20 to 39, P-TEST, P-RESERVED unread. |
| 2026-10-23 | WP1.0 confirm read once on P-CONFIRM j = 0 to 19 | +$5,186 a seed over the tuned edit, p = 0.002, 14 of 20 seeds better; ranking flips under staff cost x2 (docs/wp10_confirm.md). Criterion met. |
| 2026-10-23 | WP1.0 frozen (docs/wp10_freeze.md) | Model fingerprint 0007665628b13588. Final development run next on P-DEV j = 50 to 59. P-TEST untouched. |
