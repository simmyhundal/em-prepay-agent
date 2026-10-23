# WP1.0 final development run (P-DEV j = 50 to 59): criterion missed

[Back to the README](../README.md) · [freeze declaration](wp10_freeze.md) · [confirm](wp10_confirm.md) · [hypothesis loop](wp10_loop.md) · [seeds](seeds.md) · data: `experiments/wp10/final_dev.json`

Run 2026-10-23 as declared in the [freeze](wp10_freeze.md): frozen WP1.0 (model `0007665628b13588`, unchanged) against the tuned claim edit on ten development seeds (4051 to 4420) that no hypothesis had read. Real decisions, real score P1.0, net dollars summed over the ten seeds. This is a development run, not a test.

**Result: the declared criterion is missed.** Mean paired gain over the tuned edit **$2,063 a seed** (bar: $3,000 and one-sided p below 0.05); sum $20,630; p = 0.093 (one-sided); 7 of 10 seeds better.

| Arm | Sum | Median seed | Seeds above 0 | Largest seed's share |
|---|---|---|---|---|
| pay-all | $0 | $0 | 0 | |
| **WP1.0 (frozen)** | **$174,324** | $17,926 | 8 | 27% |
| WP1.0 without the prior | $169,616 | $16,682 | 8 | 29% |
| hand rule C1 | $129,321 | $12,206 | 9 | 26% |
| tuned claim edit | $153,695 | $14,612 | 10 | 26% |

## Reading it
- WP1.0 is ahead of the edit again, but by less than the bar, and the ten-seed spread (standard deviation about $4,600 a seed) is too wide to call a gain of $2,000 a seed. No single seed is the story, but the largest seed carries 27% of the total here (the confirm's was 11%); these ten seeds are smaller (total $174k for ten, against $601k for twenty).
- **Pooling is not a rescue.** The confirm and this run together (30 seeds) show a mean gain of $4,145 a seed (one-sided p = 0.0007). That pool was not declared in advance and combines a read that passed with one that did not; it is reported for context. The honest summary is: the gain over a no-chart rule is probably positive and probably between $2,000 and $5,000 a seed, and the pre-declared development bar is not met.
- **The ranking depends on cost assumptions.** At staff cost x2 the edit wins ($99,367 against $56,940); at staff x2 and abrasion x2 WP1.0 is negative ($-16,920) and the edit is $86,667. WP1.0 pends 4,916 claims against 2,592 denials by the edit, and pays $117k of staff time and $74k of abrasion against $54k and $13k.
- **What it catches is still the planted pattern:** $340,279 of $405,515 prevented (84%) is phantom or impossible-day claims (**easier by construction**; the chart is in hand and the generator plants the pattern).

## What this means for the process
The freeze says a miss reopens the core stories at no cost (no fresh seed was spent). P-TEST and P-RESERVED are unread. Open questions for the reopen, none run yet: whether the cap (10) and the zero floor are right when staff cost is higher; whether a cheaper pend (no chart review for NO_RECORD-prone clinicians) is possible; whether level upcoding can be priced to pay at all (the loop found it cannot under P1.0); and the P1.0 cost parameters themselves (issue 7), which decide the ranking. WP1.0 is **not** declared passed; issue 5 stays open.
