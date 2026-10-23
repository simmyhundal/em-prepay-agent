# Reference arms on prepay development seeds

[Back to the README](../README.md) · [plan](prepay_plan.md) · [score P1.0](score_prepay.md)

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
- Not yet: confirm-pool reads, the workflow, the agent, a daily pend cap.
