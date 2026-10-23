# Reference arms on prepay development seeds

[Back to the README](../README.md) · [plan](prepay_plan.md) · [score P1.0](score_prepay.md)

## First guesses

Ten development seeds of pool P-DEV (data 4.2, seeds 2001 + 41j, j = 0 to 9), free run, `python eval/run_prepay_reference.py`, 2026-10-23. Role in the registry: select (for the claim edits and the provider-level adjustment), but **no threshold was tuned yet**: every threshold is the first guess (daily maximum 30, member maximum 4 in 30 days, provider share above peers by 0.20 with 20 earlier claims). Score P1.0 in net dollars, summed over ten seeds; overbilled dollars available over the ten seeds: $2,740,125.

| Arm | Score (sum) | Median seed | Seeds above zero | Pended | Denied | Wrongful adjustments |
|---|---|---|---|---|---|---|
| pay_all | $0 | $0 | 0 of 10 | 0 | 0 | 0 |
| edits | $-336,544 | $-20 | 5 of 10 | 0 | 7185 | 4482 |
| auto_all | $-65,130,441 | $-6,379,785 | 0 of 10 | 0 | 0 | 594153 |
| auto_provider | $-1,592,973 | $-121,618 | 0 of 10 | 0 | 0 | 14553 |
| oracle | $1,012,785 | $93,992 | 10 of 10 | 30613 | 9698 | 0 |

Reading it:
- **Pay-all** is zero by construction. **The oracle** (answer key; pends only claims whose resolved pend adds to the score, through the real office) is the ceiling: an upper bound, not an arm.
- **Automatic adjustment of every level 4 and 5 claim** loses millions: it underpays the many correct claims, and P1.0 counts every dollar owed and not paid as a loss (the payer cannot count a wrongful adjustment as saved).
- **The provider-level adjustment and the claim edits** are untuned first guesses; they lose or roughly break even. Their tuning is the next step, on the development pool only.
- Numbers depend on assumptions in [score P1.0](score_prepay.md) (appeal rate, abrasion per wrongful adjustment, interest). Each seed's sensitivity grid is in `experiments/prepay_reference/results.json`.

## Tuned (2026-10-23)

Rules: thresholds chosen on **select** seeds P-DEV j = 10 to 19 (seeds 2411 to 2780), each arm's grid scored there; the winner (or "never act", zero, if no setting is above zero) was written to `experiments/prepay_reference/tuning.json` before anything else was read; then read **once** on P-DEV j = 20 to 29 (seeds 2821 to 3190), a declared hold-out inside the development pool. P-CONFIRM, P-TEST and P-RESERVED were not touched. Code: `eval/tune_prepay_reference.py`. Grids: edits, 2 keys x 9 daily maxima x 5 member maxima = 90 settings; provider-level adjustment, 2 keys x 6 deltas x 3 minimum histories = 36 settings (126 tried).

One change the grid needed: the stream's "provider" is the **billing NPI, a group** (74 groups, 216 clinicians in a dataset), and the postpay screen scores the **rendering clinician**. Both keys are in the grids (`by="provider"` is the old behaviour, so the first-guess table above still reproduces; checked on seed 2001).

| Arm | Select j = 10 to 19 (sum) | Hold-out j = 20 to 29 (sum) | Hold-out median seed | Seeds above zero | One seed's share of the total |
|---|---|---|---|---|---|
| pay-all | $0 | $0 | $0 | 0 of 10 | |
| claim edits, first guess (group key, max 30/day, 4 per member) | not scored | $-363,599 | $-19,042 | 2 of 10 | |
| **claim edits, tuned** (clinician key, max 20 per day per clinician per service date, member max 6 which never binds) | $227,176 | **$203,877** | $25,940 | 9 of 10 | 19% (largest seed) |
| provider-level adjustment, first guess | not scored | $-1,885,881 | $-182,699 | 0 of 10 | |
| **provider-level adjustment, tuned** | best setting $-54,714 (it adjusts nothing: the cost is the $0.05 screen) | "never act" = pay-all, **$0** | $0 | | |
| oracle | not run | $995,497 | $95,734 | 10 of 10 | 14% |

Reading it:
- **The tuned claim edit is the one thing that beats pay-all, and what it catches is planted.** 94% of the $299,581 it prevented ($280,705) is claims of the two phantom kinds (`impossible_days`, `not_rendered`); it prevents 9.7% of the overbilled dollars (level upcoding is untouched). The generator makes impossible-day clinicians bill far more than the honest maximum, so a cap at 20 a day separates them; this is **easier by construction**. The result is sharp in the threshold: the same rule at 15 a day loses on 3 of 10 select seeds (wrongful denials of busy honest clinicians), at 30 a day gains about 45% as much. Gains are spread over seeds (largest seed 19%; one seed is negative); this is not a one-seed finding. A real payer's daily volumes are not this clean.
- **No setting of the provider-level adjustment beats pay-all**, on either key, at any share-above-peers threshold from 0.05 to 0.4 or history from 20 to 300 claims. The tuned arm is therefore pay-all. The share of level 4 and 5 visits does not separate upcoders from honest clinicians well enough to pay for the honest providers' wrongful adjustments under P1.0 (a wrongful adjustment loses the dollars owed and costs $100 of abrasion and appeal time in expectation).
- The edits at their chosen setting under the sensitivity grid (staff and abrasion x0.5 to x2): $127k to $242k, always above zero.
- Compared at equal review: the edits request no charts at all (no pends, 3,333 denials, 206 of them wrongful). The oracle pends about 3,000 claims per seed.
- Multiple comparisons: 126 settings were scored on the select seeds; the hold-out read was one declared read per arm, which is why the hold-out, not the select sum, is the number to quote.
