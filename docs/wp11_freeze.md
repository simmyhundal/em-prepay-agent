# WP1.1 freeze declaration

[Back to the README](../README.md) · [confirm](wp11_confirm.md) · [loop](wp11_loop.md) · [seeds](seeds.md)

Declared 2026-10-23, before the final development run.

**Frozen.** `src/wp10.py`, `src/provider_prior.py`, `src/prepay_env.py`, `src/claim_stream.py` as at the commit of this page; the rule fitted on P-DEV j = 30 to 39 (fingerprint `0007665628b13588`); cap 10; **pend floor $15**; expired pends denied; wait limit 45 days; score P1.0 unchanged. `FROZEN` in `eval/wp11_loop.py` records the floor. A change is WP1.2.

**Final development run.** P-DEV2 j = 40 to 59 (seeds 9641 to 10420, never read), fresh and free: frozen WP1.1, WP1.0 (the previous workflow, re-run on the same seeds), the tuned claim edit, hand rule C1, pay-all. Command: `python eval/wp11_loop.py final --record`.

**Pass criterion.** The same as the confirm: mean paired gain over the tuned edit of at least $3,000 a seed, one-sided paired p below 0.05, and a positive total gain in all nine cost cells. A miss reopens the core stories. P-TEST and P-RESERVED are not built or read. The paid agent run needs Simmy's approval, an estimate and a cap.
