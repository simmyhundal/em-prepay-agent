# WP1.1 hypothesis loop (P-DEV2 select seeds)

[Back to the README](../README.md) · [plan](wp11_plan.md) · [WP1.0 final run](wp10_final_dev.md) · [seeds](seeds.md) · code: `eval/wp11_loop.py` · data: `experiments/wp11/loop.json`

After the WP1.0 miss, the core stories were reopened ([plan](wp11_plan.md)). Four single changes to WP1.0 were scored on 20 new development seeds (P-DEV2 j = 0 to 19, seeds 8001 to 8738), real decisions through score P1.0 and its nine-cell cost grid (staff and abrasion each x0.5, x1, x2). Net dollars summed over twenty seeds; "gain" is the paired gain over the tuned claim edit per seed. P-CONFIRM, P-TEST and P-RESERVED were not touched. Bonferroni bar for four changes: 0.05 / 4 = 0.0125.

| Arm | Sum | Seeds above 0 | Gain over the tuned edit, per seed | One-sided p | Mean gain over the nine cost cells, per seed | Worst cell, per seed |
|---|---|---|---|---|---|---|
| pay-all | $0 | 0 | $-17,642 | | | |
| tuned claim edit | $352,845 | 17 | | | | |
| hand rule C1 | $293,218 | 17 | $-2,981 | | | |
| WP1.0 (floor $0) | $358,997 | 15 | $308 | 0.42 | $-2,301 | $-15,342 |
| **H11a pend floor $15** | **$484,195** | 17 | **$6,567** | 6e-6 | $5,691 | $1,309 |
| H11b pend floor $30 | $475,713 | 18 | $6,143 | 1e-6 | $5,442 | $1,935 |
| H12 fit on 20 seeds | $374,752 | 16 | $1,095 | 0.22 | $-1,282 | $-13,171 |
| H13 larger model | $318,684 | 15 | $-1,708 | 1.0 | $-5,039 | $-21,691 |

Pick rule (declared in the plan): the highest mean gain over the nine cost cells. That is **H11a, a pend floor of $15**, which becomes WP1.1 (rule fitted on P-DEV j = 30 to 39, cap 10, expired pends denied; only the floor changed).

## What the loop taught
- **On new seeds WP1.0 was no better than the edit** (+$308 a seed, p = 0.42), and in four of nine cost cells worse. The earlier confirm and final run (+$5,186, +$2,063) were not stable evidence of a lead.
- **The floor is the repair.** At $15 WP1.1 pends 8,445 claims instead of 11,018 and has 435 wrongful pends instead of 1,176, keeping $729k of the $757k of phantom and impossible-day dollars; staff cost falls from $258k to $199k and abrasion from $197k to $48k. It is ahead of the edit in every one of the nine cost cells (worst +$1,309 a seed). The same floor did not help in the WP1.0 loop, when the rule was trained on all pends; after training on resolved pends only, the rule's dollar estimates are good enough to threshold. A lead worth confirming, not a result.
- **More fit data and a larger model did not help** (H12, H13). **Easier by construction:** most of the money is still the planted impossible-day pattern, and the floor works by pending fewer of the claims where the chart is likely to find nothing.
- Settings tried: two floors, one fit size, one model size (four changes). The choice among floors rests on twenty seeds; the declared confirm on twenty others comes next ([declaration](wp11_confirm_declaration.md)).
