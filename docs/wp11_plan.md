# WP1.1 plan: reopening the core stories after the WP1.0 miss

[Back to the README](../README.md) · [WP1.0 final development run](wp10_final_dev.md) · [seeds](seeds.md) · [process](process.md)

Written 2026-10-23, before any WP1.1 run. WP1.0 passed its confirm (+$5,186 a seed over the tuned claim edit) and missed its final development run (+$2,063 a seed, bar $3,000, p = 0.093), and its lead over the edit flips at staff cost x2 ([confirm](wp10_confirm.md), [final run](wp10_final_dev.md)). P-TEST and P-RESERVED are unread.

**Core stories (what WP1.1 tries to fix)**
1. The gain over a no-chart rule is small and fragile to staff cost. Test whether a higher pend floor, more fit data and a better-sized model make it hold under the cost grid.
2. Say how much of the gain is a mechanical effect of pending fewer claims: every candidate is read against the tuned edit, the hand rule C1 and a same-count random control.

**Seeds.** New development pool P-DEV2 (seeds 8001 + 41j, j = 0 to 59): select j = 0 to 19; one declared confirm j = 20 to 39; final development run j = 40 to 59. The rule is fitted on P-DEV j = 30 to 49 (new arm WP1.1, so no earlier hold-out is spoiled; WP1.0's own seeds stay with WP1.0).

**Yardsticks.** Pay-all (zero); the tuned claim edit; hand rule C1; WP1.0 re-run freshly on the same seeds (it is free); the oracle at 10 pends a day.

**Hypotheses (all against WP1.0, one change each, scored on select j = 0 to 19)**
- H11 pend floor of $15 and $30 (WP1.0: $0).
- H12 fit on 20 seeds instead of 10.
- H13 larger model (depth 6, 300 rounds).
The pick rule is declared now: the candidate with the highest mean paired gain over the tuned edit across the nine staff-and-abrasion cost cells (x0.5, x1, x2 each), not only at base cost. Bonferroni bar: 0.05 divided by the number of changes tried (3 changes plus the floor settings). One declared confirm; freeze; final development run; the paid agent run stays ask-first.
