# Pend

[Back to the concepts](README.md) · [glossary](../glossary.md)

**What it means.** Holding a claim unpaid while the payer asks the provider for the medical record (the chart).

**Why it exists.** A payer cannot tell from the claim alone whether a visit was billed at the right complexity. Asking for the chart settles it before money leaves, but it costs staff time and burdens the provider.

**Example.** A 99215 claim from a clinician with 22 visits on one service date is pended; the chart comes back and shows a shorter, simpler visit, so the claim is paid at 99213.

**Where to find it.** `src/prepay_env.py` (`resolve_pend`), [score P1.0](../score_prepay.md)
