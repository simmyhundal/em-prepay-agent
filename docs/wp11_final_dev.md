# WP1.1 final development run (P-DEV2 j = 40 to 59): criterion met

[Back to the README](../README.md) · [freeze](wp11_freeze.md) · [confirm](wp11_confirm.md) · [loop](wp11_loop.md) · [seeds](seeds.md) · data: `experiments/wp11/final_dev.json`

Run 2026-10-23 as declared in the [freeze](wp11_freeze.md): frozen WP1.1 (pend floor $15, cap 10) and the previous workflow WP1.0, both freshly run, against the tuned claim edit, on twenty development seeds (9641 to 10420) that no hypothesis had read. Real decisions, score P1.0, net dollars summed over twenty seeds. This is a development run, not a test. (A first attempt crashed on a half-written cache file before any result was produced; the cache write was made atomic and the run repeated, so no seed was read twice.)

**Result: the declared criterion is met.** Mean paired gain over the tuned edit **$6,837 a seed** (bar $3,000); one-sided p = 7e-6; 18 of 20 seeds better; positive in all nine cost cells (worst +$2,106 a seed).

| Arm | Sum | Median seed | Seeds above 0 | Largest seed's share | Worst-cell gain over the edit, per seed |
|---|---|---|---|---|---|
| pay-all | $0 | $0 | 0 | | $-20,230 |
| tuned claim edit | $335,898 | $14,961 | 16 | 13% | |
| hand rule C1 | $279,352 | $12,650 | 16 | 14% | $-5,505 |
| WP1.0 | $370,057 | $15,149 | 16 | 15% | $-12,135 |
| **WP1.1** | **$472,630** | $21,947 | 17 | 12% | **$+2,106** |

## Reading it
- **The earlier workflow again lands near the edit** ($34,159 over twenty seeds); the whole gain is the floor. WP1.1 pends 8,137 claims (403 wrongful) against WP1.0's 10,480 (972), with abrasion of $43k against $172k.
- **Still the planted pattern:** $703,175 of $721,412 prevented (97%) is phantom or impossible-day claims; WP1.1 prevents 12.4% of overbilled dollars (the edit: 8.4%). **Easier by construction:** the chart is in hand before payment and the generator plants the pattern.
- Two seeds are worse than the edit (by at most $433); the largest seed carries 12% of the total.
- Two passes in a row on seeds the floor was not chosen on make WP1.1 the first prepay workflow to clear the bar. It has **not** been tested: P-TEST (6001 + 41j) and P-RESERVED are unbuilt and unread.
