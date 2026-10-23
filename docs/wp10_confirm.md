# WP1.0 confirm result (P-CONFIRM, 20 seeds)

[Back to the README](../README.md) · [declaration](wp10_confirm_declaration.md) · [hypothesis loop](wp10_loop.md) · [seeds](seeds.md) · data: `experiments/wp10/confirm.json` · code: `eval/wp10_confirm.py`

Read once on 2026-10-23, as declared before the seeds were built: WP1.0 (the frozen H7 workflow, model `0007665628b13588`) against the tuned claim edit (denies when one clinician has more than 20 claims for a service date), on P-CONFIRM j = 0 to 19, real decisions through the real score P1.0. Net dollars; "sum" is over the 20 seeds. Nothing was refitted on these seeds.

**Result: the declared criterion is met.** The mean paired gain was **$5,186 a seed** (declared bar: $3,000 and one-sided p below 0.05); sum $103,713; one-sided paired t p = 0.002; 14 of 20 seeds better, 6 worse.

| Arm | Sum | Median seed | Seeds above 0 | Largest seed's share |
|---|---|---|---|---|
| pay-all | $0 | $0 | 0 | |
| **WP1.0** | **$601,382** | $29,733 | 18 | 11% |
| WP1.0 without the prior | $581,778 | $27,951 | 18 | 12% |
| hand rule C1 (pend at 20 claims a day) | $424,865 | $20,598 | 19 | 11% |
| tuned claim edit | $497,669 | $24,354 | 19 | 10% |

## What to make of it
- **It is not one seed.** The largest seed carries 11% of the total; two of twenty seeds are negative for WP1.0.
- **The gain over the edit is real but modest, and the select seeds understated it** ($1,513 a seed there, p = 0.47). The twenty paired differences have a standard deviation of about $7,100, so the p-value is from one declared test; the selection read was a noisy preview.
- **What it catches is still the planted pattern.** $990,169 of the $1,136,469 WP1.0 prevented (87%) is phantom or impossible-day claims. It prevents 17.7% of overbilled dollars (the edit: 10.8%): a few more level differences, found by a chart rather than a count. **Easier by construction:** the chart is in hand before payment, the generator plants the impossible-day pattern, and the office returns NO_RECORD for phantom claims.
- **Its advantage comes from pending instead of denying.** WP1.0 pended 13,439 claims (1,048 wrongful pends, 1,080 wrongful adjustments or denials), spent $274,779 on staff and $167,532 on abrasion; the edit spent $111,944 and $29,600. WP1.0 pays more to prevent more.
- **The ranking depends on the cost assumptions.** At staff cost x2 the edit wins ($385,726 against $326,603); at abrasion x2 with staff x1 the edit wins ($468,069 against $433,850). WP1.0 leads at staff x1 or less with abrasion x1 or less. The arms are not ranked robustly; this is an assumption-driven result and the cost parameters (issue 7) are the least sourced part of P1.0.
- **The prior adds about $1,000 a seed** ($601,382 against $581,778, same sign as in the loop).
- **Pends wait.** The median pend takes 45 days (the wait limit); only honest claims pay delay interest, but a payer with a shorter prompt-pay clock would see more of that cost.
- One test, no multiple-comparison penalty applies; the 10 changes and about 59 settings in the loop were scored on other seeds.
