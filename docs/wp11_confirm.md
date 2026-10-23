# WP1.1 confirm result (P-DEV2 j = 20 to 39, 20 seeds)

[Back to the README](../README.md) · [declaration](wp11_confirm_declaration.md) · [loop](wp11_loop.md) · [seeds](seeds.md) · data: `experiments/wp11/confirm.json`

Read once on 2026-10-23 as declared: frozen WP1.1 (WP1.0's rule, model `0007665628b13588`, pend floor $15, cap 10) against the tuned claim edit, real decisions, score P1.0, net dollars summed over twenty seeds (8821 to 9600). Nothing was refitted.

**Result: the declared criterion is met on all three parts.** Mean paired gain **$8,589 a seed** (bar $3,000); one-sided paired t p = 4e-8; **20 of 20 seeds better**; the total gain is positive in **all nine cost cells** (worst: staff x2 with abrasion x2, +$2,792 a seed).

| Arm | Sum | Median seed | Seeds above 0 | Largest seed's share | Worst-cell gain over the edit, per seed |
|---|---|---|---|---|---|
| pay-all | $0 | $0 | 0 | | $-26,807 |
| tuned claim edit | $466,080 | $21,088 | 20 | 11% | |
| hand rule C1 | $394,966 | $17,916 | 20 | 11% | $-6,928 |
| WP1.0 (floor $0) | $533,532 | $24,687 | 19 | 12% | $-12,080 |
| **WP1.1 (floor $15)** | **$637,853** | $27,963 | 20 | 11% | **$+2,792** |

## Reading it
- WP1.1 pends 10,130 claims (421 wrongful pends, 211 wrongful adjustments) against WP1.0's 12,672 (1,042 and 1,216); staff cost $211k against $268k, abrasion $45k against $181k; it prevents $912k against $1,087k. Fewer, better-chosen pends.
- **It is not one seed**: the largest seed carries 11% of the total, and the smallest paired gain over the edit is +$1,484.
- **What it catches is still the planted pattern.** $892,500 of the $911,786 it prevented (98%) is phantom or impossible-day claims; it prevents 15.9% of overbilled dollars (the edit: 10.8%). **Easier by construction:** the chart is in hand before payment, the generator plants the impossible-day pattern and returns NO_RECORD for phantom claims.
- **The honest limit:** the floor was chosen on twenty seeds and confirmed on twenty others, which is one declared test; WP1.0 had also passed its first confirm and then failed (the evidence gets harder, not softer, at the final development run). Next: the [freeze](wp11_freeze.md) and the final development run on P-DEV2 j = 40 to 59.
