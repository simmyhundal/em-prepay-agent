# True test of release P1: declared before the run

[Back to the README](../README.md) · [WP1.1 freeze](wp11_freeze.md) · [AP1.0](ap10.md) · [seeds](seeds.md)

Declared 2026-10-25, before P-TEST (6001 + 41j) is built or read. Simmy's approval, given in chat on 2026-10-25: **a $1.00 cap for the whole release, on ten test seeds** (P-TEST j = 0 to 9, seeds 6001 to 6370; not on development seeds), and the key in `.env`.

**Arms, run once.** Free: the frozen workflow WP1.1, the previous workflow WP1.0, the tuned claim edit, the hand rule C1, pay-all. Paid: the agent AP1.0 with Claude Haiku 5.5 (`claude-haiku-5-5`, $0.10 / $0.50 per million tokens), one model call per day on which WP1.1 advises a pend, effort `low`, one tool. The $1.00 cap is global: the run stops calling the model when its measured cost reaches the cap and every later day follows the workflow's advice (the result states how many days the model decided). No retries, no second run, no tuning on these seeds.

**Estimate (logged before spending).** Token counts measured with the free counter on 16 development days: about 900 input tokens a call. Output with adaptive thinking at low effort is assumed at 250 to 600 tokens. About 200 consulted days a seed. That is about $0.0002 to $0.0004 a call, **$0.04 to $0.08 a seed, $0.4 to $0.8 for ten seeds**, under the cap. A per-seed limit of $0.12 stops any one seed from taking the budget.

**Pass criteria.** Workflow: the same as the confirm: mean paired gain over the tuned edit of at least $3,000 a seed, one-sided p below 0.05, positive total gain in all nine cost cells. Agent: no bar beyond cost; reported as the paired difference from WP1.1 on the same seeds with its p-value, and how often the model overrode the advice. A miss or a null agent result is reported as such. The earlier agent is never re-run; the comparison with WP1.0 is the workflow's.

**Scope of the agent, stated plainly.** The first design (`provider_history`, per-claim `read_chart` and `adjust` turns) was estimated at $19 a ten-seed run with Haiku 5.5 and was cut to fit the cap: the model sees a one-line summary of the advised pends and up to three near-misses, and chooses which to pend; the rules read every returned chart and decide. So this agent can only add or drop pends; it cannot adjust levels or look up a clinician's history.
