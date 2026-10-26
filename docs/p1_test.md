# True test of release P1 (P-TEST j = 0 to 9)

[Back to the README](../README.md) · [declaration](p1_test_declaration.md) · [WP1.1 freeze](wp11_freeze.md) · [AP1.0 design](ap10.md) · [seeds](seeds.md) · data: `experiments/p1_test/`

Run once on 2026-10-25 on ten fresh seeds (6001 to 6370, each about 216 providers), as declared before the seeds were built. Score P1.0, real decisions, net dollars summed over ten seeds. **Simmy's approval: $1.00 cap for the release, ten test seeds, Haiku 5.5. The run cost $0.30** (measured from the API's token counts, `experiments/p1_test/agent_usage_<seed>.json`). The pool is now burned for the workflow and agent lines.

## Workflow: the declared criterion is met
WP1.1 beat the tuned claim edit by **$5,709 a seed** (bar $3,000), one-sided paired p = 0.002, **9 of 10 seeds better**, and the total gain is positive in **all nine cost cells** (worst +$1,813 a seed).

| Arm | Sum | Median seed | Seeds above 0 | Largest seed's share | Worst-cell gain over the edit, per seed |
|---|---|---|---|---|---|
| pay-all | $0 | $0 | 0 | | $-15,628 |
| tuned claim edit | $123,672 | $10,247 | 8 | 22% | |
| hand rule C1 | $102,456 | $8,345 | 8 | 23% | $-4,358 |
| WP1.0 (the first workflow) | $130,677 | $8,503 | 8 | 28% | $-11,562 |
| **WP1.1 (frozen)** | **$180,757** | $14,862 | 9 | 22% | **$+1,813** |
| AP1.0 (agent, Haiku 5.5) | $152,512 | | 10 of 10 positive but one ($-8,313) | | |

WP1.0 is $7,000 above the edit over ten seeds, not distinguishable: the floor is again the whole gain. The tuned edit's score is lower here than on the development seeds ($124k against $336k to $466k for twenty); the test seeds carry less of the planted impossible-day pattern, so every arm earns less (the oracle was not run on these seeds). WP1.1 pends 3,393 claims (184 wrongful pends, 61 wrongful adjustments); $284,570 of its $290,539 prevented (98%) is phantom or impossible-day claims, so it is still the planted pattern that pays (**easier by construction**: the chart is in hand and the generator plants the pattern).

## Agent: worse than the workflow it mirrors
AP1.0 scored **$152,512 against WP1.1's $180,757: $-2,824 a seed** (paired two-sided p = 0.002); the agent was better on 1 of 10 seeds. On 950 consulted days the model followed the workflow's advice on 712 (75%) and changed the choice on 238 (25%); its changes were almost all drops of advised pends (2,876 pends against 3,393), and the claims it dropped were worth pending. It does beat the tuned edit and WP1.0 in total, but only because it keeps most of the workflow's advice.

What this does and does not say. The agent here is deliberately small: one model call a day, one tool (`pend`), a one-line summary of the advised pends and three near-misses, low effort, Haiku 5.5, to fit the $1 cap. It could not look up a clinician's history or adjust a level, and a stronger model or a richer view might do better (Simmy's reference: Opus 5.5 at low effort on the sibling repository's ten-seed tests runs under $2). That experiment was not run; this result is for this agent only. The first multi-turn design was estimated at about $19 with Haiku 5.5 for ten seeds and was cut. The cap was never reached: all ten seeds ran with the model, no day fell back to the advice for cost.

## What the release shows, and does not
- A chart-requesting workflow with a learned pend rule and a $15 floor beat a no-chart claim edit on development seeds (twice) and on fresh test seeds, positive under every cost assumption tried; most of the money is the planted pattern.
- Level upcoding is not caught profitably under P1.0 (the prior's claim-level signal is weak and a pend costs more than a level recovers).
- A cheap model given the workflow's advice does worse than following the advice.
- Not tested: the oracle on these seeds, a real payer's data, providers that change behaviour when pended, commercial prompt-pay clocks.
