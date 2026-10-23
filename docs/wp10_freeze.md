# WP1.0 freeze declaration

[Back to the README](../README.md) · [confirm result](wp10_confirm.md) · [hypothesis loop](wp10_loop.md) · [seeds](seeds.md)

Declared 2026-10-23, before the final development run. The [confirm](wp10_confirm.md) met its declared bar ($5,186 a seed against $3,000; p = 0.002), so WP1.0 is frozen as it stood for the confirm.

**Frozen.** `src/wp10.py`, `src/provider_prior.py`, `src/prepay_env.py`, `src/claim_stream.py` and the parameters in them: prior refreshed weekly (minimum 3,000 claims), ten features, gradient-boosted rule fitted on P-DEV j = 30 to 39 on resolved pends only (model fingerprint `0007665628b13588`), daily cap 10, pend when estimated value is above $0, expired pends denied, wait limit 45 days, score P1.0 unchanged. Further behaviour changes go behind a new version (WP1.1) and a new score or data version is a new module.

**Final development run.** P-DEV j = 50 to 59 (seeds 4051 to 4420, never read by any hypothesis; registry arm `WP1.0-final-dev`), freshly run and free: frozen WP1.0, the tuned claim edit, the hand rule C1, WP1.0 without the prior, pay-all. There is no earlier workflow to re-run: WP1.0 is the first prepay workflow, and the same-cap control is the loop's (C1, C2, C3). Command: `python eval/wp10_confirm.py --final-dev --record`.

**Pass criterion.** The same as the confirm: mean paired gain over the tuned claim edit of at least $3,000 a seed and a one-sided paired t-test p below 0.05. This is a development run, not a test: these seeds are development data, and it only guards against a result that depended on the select and confirm seeds. If it misses, the core stories reopen (no fresh seed has been spent).

**Not yet done, by design.** P-TEST (6001 + 41j) and P-RESERVED are not built or read. The agent AP1.0 (issue 6) is not started: it is a paid run and needs Simmy's approval, an estimate and a cap.
