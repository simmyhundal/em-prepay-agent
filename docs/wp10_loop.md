# WP1.0 hypothesis loop (select seeds)

[Back to the README](../README.md) · [plan](prepay_plan.md) · [score P1.0](score_prepay.md) · [seeds](seeds.md) · code: `src/wp10.py`, `src/provider_prior.py`, `eval/wp10_loop.py`, `eval/wp10_eval.py` · data: `experiments/wp10/ledger.json`

Written 2026-10-23. Arm: provider prior (the postpay screen eb_upper_t, refreshed weekly from claims received so far, per rendering clinician), a learned rule that estimates what pending each claim is worth, a daily pend cap of 10, rules on the returned chart (pay the supported level; no record denies; no usable answer by day 45 denies). API-free. Fit on P-DEV j = 30 to 39, hypotheses scored on select seeds P-DEV j = 40 to 49 (seeds 3641 to 4010), P-CONFIRM, P-TEST and P-RESERVED untouched. Score P1.0, net dollars summed over the ten select seeds; the screen ($0.05 a claim, about $5,200 a seed) is charged to every arm except pay-all.

## Results (sum of 10 seeds; paired difference against H7)
| Arm | Sum | Median seed | Seeds above 0 | vs H7 | paired t p |
|---|---|---|---|---|---|
| pay-all | $0 | $0 | | | |
| screen only | $-51,984 | | 0 | | |
| H1 learned rule (regression on pend value), unresolved pends valued as honest | $6,021 | $-3,951 | 4 | $-181,623 | 0.009 |
| H2 H1, expired pends paid as billed | $-51,993 | | 0 | $-239,638 | 0.009 |
| H3 H1 without the prior | $13,179 | | 4 | | |
| H4 H1, pile-on features only | $-36,725 | | 1 | | |
| **H7 train on resolved pends only (the WP1.0 candidate)** | **$187,644** | $12,942 | 8 | | |
| H8 H7 without the prior | $177,261 | $11,782 | 8 | $-10,383 | 0.0013 |
| H9 H7, cap 5 | $160,840 | | 8 | $-26,805 | 0.02 |
| H10 H7, cap 30 | $190,986 | | 8 | $+3,342 | 0.049 |
| C1 hand rule: pend a claim when its clinician already has 20 that service date | $144,946 | $11,506 | 8 | $-42,698 | 0.14 |
| C2 random pends, same count as H7 (billed 99214 or 99215) | $-639,477 | | 0 | | |
| C3 prior only, top 10 a day among 99214 and 99215 | $-3,944,762 | | 0 | | |
| C4 tuned claim edit (denies, no chart) | $172,511 | $13,756 | 8 | $-15,133 | 0.47 |
| C5 oracle at 10 pends a day (answer key) | $856,541 | $87,325 | 10 | | |

Hypotheses counted: 10 changes (H1 to H10) and about 59 further settings scored on the select seeds (cap and floor grids, threshold rules, a classifier threshold). The Bonferroni bar is 0.05/10 = 0.005 for the changes (0.0007 if the settings count). Only the **H7 versus H1 repair** (p = 0.009, a lead at the strict bar) and the **prior's contribution H7 versus H8** (p = 0.0013, a result at the 10-change bar, not at the strict bar) get near it. H10 (cap 30) is a lead, not a result, and the cap stays 10.

## What the loop taught
- **The learned rule was wrong until the labels were fixed (H1 to H7).** Pends that come back with no answer say nothing about the visit; valuing them as honest (H1) or paying them (H2) taught the rule the valuer's assumption. Training on resolved pends only (H7) lifts it from $6k to $188k. 20% of pends are unresolved; this is the single largest lever found.
- **Where the money is: planted phantom claims.** The rule's pends are mostly claims of clinicians billing more visits in a day than is possible (`impossible_days`), plus never-rendered claims. Level upcoding is barely touched: the prior's per-claim AUC for an overbilled 99214 or 99215 is 0.54, and even the top 1% by prior (33% overbilled) loses $54 to $79 per pend under P1.0, because a pend costs about $21 of staff time and an honest pend $44 of abrasion against about $25 to $45 recovered per overbilled level. **Easier by construction:** the generator plants the impossible-day pattern and the lab-line covariate; a real payer's volumes are not this clean.
- **WP1.0 is not clearly better than a rule with no chart.** H7 beats the tuned claim edit by $15,133 over ten seeds (p = 0.47) and the hand rule C1 by $42,698 (p = 0.14). The pend's advantage (a chart settles a busy honest clinician) is small here because few honest clinicians trip the threshold. This is the question the confirm tests.
- **The prior adds about $1,000 a seed** (H7 against H8), consistent with its weak claim-level signal.
- The same-cap controls (C2, C3) are far below zero: forcing pends at 10 a day is a loss; the gain is the learned choice of which to pend, not the cap. The cap binds little (H10).
- Not checked: an assumed `EXPIRED_POLICY` of deny (H2 shows pay-billed is far worse for this rule); a P_APPEAL sensitivity for WP1.0; behaviour under the other 50 dev seeds.
