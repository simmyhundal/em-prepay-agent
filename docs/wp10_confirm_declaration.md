# WP1.0 confirm: declared before the read

[Back to the README](../README.md) · [hypothesis loop](wp10_loop.md) · [seeds](seeds.md)

Declared 2026-10-23, before any P-CONFIRM seed is generated or read.

**What is confirmed.** One workflow, WP1.0 = hypothesis H7 of the [loop](wp10_loop.md): the weekly-refreshed eb_upper_t prior, all ten features, the gradient-boosted rule fitted on P-DEV j = 30 to 39 (seeds 3231 to 3600) on resolved pends only with the labels of `src/wp10.py`, daily cap 10, pend when the estimated value is above $0, expired pends denied. Nothing is refitted or re-chosen on the confirm seeds.

**Seeds.** P-CONFIRM j = 0 to 19 (seeds 2002 + 41j). The pool flips from `fresh` to `in_use` in the registry in the same commit as this page; the other 20 seeds stay unread.

**The one comparison.** WP1.0 against the tuned claim edit (clinician key, more than 20 claims by one clinician for one service date, member maximum 6; [reference arms](prepay_reference_arms.md)), paired per seed, net score P1.0, real decisions through the real score (not the loop's cached tables). Secondary, reported but not decisive: against pay-all, against the hand rule C1 of the loop, against the same arm without the prior (H8).

**Pass criterion ("marked improvement").** Mean paired gain of at least $3,000 per seed (about $60,000 over twenty seeds) and a one-sided paired t-test p below 0.05. On the select seeds the gap was $1,513 a seed (p = 0.47), so a miss is the expected outcome; it will be reported as a miss.

**Also reported.** Per-seed scores, seeds above zero, share of the total carried by the largest seed, dollars from phantom claims versus level differences, pends, wrongful pends, days to payment, and the sensitivity grid (staff and abrasion x0.5 to x2). Power: with a paired spread near $4,000 a seed on the select seeds, twenty seeds detect a gain of roughly $2,500 a seed.

**What happens after.** Pass or miss, the result goes in `docs/wp10_confirm.md` and the decision log. Only then the freeze declaration; P-TEST and P-RESERVED are not touched by this step.
