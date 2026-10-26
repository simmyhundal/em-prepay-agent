# Reflection on release P1: the deepest flaws of this system

[Back to the README](../README.md) · [true test](p1_test.md) · [release notes](releases/P1.md) · [score P1.0](score_prepay.md)

What is by construction, what is unverified, what a sceptic would attack, and what is not measured. Each flaw worth fixing has an issue.

**The data.** About 98% of the money WP1.1 prevents is claims the generator planted as never rendered or impossible in volume, and the cheapest rule that denies a clinician's twenty-first claim of a day earns most of it. The result is therefore mostly a statement about the generator, not about upcoding. Level upcoding (the common real problem) cannot be caught profitably: the prior's per-claim signal is weak (AUC 0.54) and a pend costs more than a level recovers. The chart is in hand before payment, so no extrapolation is needed; real offices lose, delay and dispute charts. Providers never change behaviour once pended.

**The score.** Every cost parameter (staff minutes, abrasion, appeals at 50%, 18% interest, a 45-day wait, denial on no answer) is an assumption; the ranking of WP1.1 against the edit holds in all nine cost cells tried but flips at staff cost x2 for the first workflow, and the nine cells move only two groups of parameters. The oracle was not run on the test seeds, so no share of the possible is stated for them.

**The statistics and seed use.** The $15 floor was chosen on twenty seeds and confirmed on twenty others; a first workflow passed its confirm and then missed, so one pass is weak evidence and three passes (confirm, final run, test) are what carry the claim. The test had ten seeds, the edit's rule was tuned on development seeds, and the totals vary by about a factor of two between seed sets.

**The arms.** The agent was cut to a one-call-a-day, one-tool design to fit a $1 cap with the cheapest model; its negative result does not say a stronger model or a richer view would lose. The agent can drop pends but cannot adjust levels or look up history.

**The process.** The workflow's labels treat no-answer pends as unknown (the largest single lever found); the registry flagged but did not block several reuses of arm names across pools. Dataset builds, caches and killed runs cost hours (a half-written cache once crashed a run).

**What is not measured.** A real payer's claim mix, commercial prompt-pay clocks, a pend notice, appeals, provider response to being pended, claims that never resolve, any customer's staffing.
