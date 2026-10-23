# Score P1.0 (prepay): every parameter, with its source or "assumption"

[Back to the README](../README.md) · [plan](prepay_plan.md) · code: `eval/score_prepay.py` (to build, issue 2)

Draft 2026-10-23. P1.0 is to prepay what score 4.0 is to postpay ([score 4.0](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/score_40.md)): **dollars prevented minus staff cost minus abrasion**, in net dollars per seed, summed over ten seeds in tables. Wages and minutes are score 4.0's where the task is the same (its sources were checked 2026-10-20 and are not rechecked here). Everything marked *assumption* has a sensitivity (x0.5 to x2) reported with the score. The score is fixed before any arm is tuned and never edited once used; a change is P1.1.

## Formula
```
P = Prevented - WrongfulLoss - StaffCost - Abrasion          (per seed)

For each claim c: billed(c) = amount paid if paid as billed; justified(c) = amount the visit supports
(0 for a claim never rendered); paid(c) = amount the arm finally paid.

Prevented    = sum over claims of (billed - paid)                 (what the arm did not pay)
WrongfulLoss = sum over claims of max(0, justified - paid)         (money owed to a provider and not paid)
```
Net money is therefore (billed - justified) on every claim the arm resolved correctly, a loss on every claim it paid too little on, and nothing for paying as billed. A wrongful denial cannot score: it adds to Prevented and WrongfulLoss by the same amount. Underpayment is netted: a claim billed below the justified level that is paid as billed gives zero, and is not credited.

## Decisions and outcomes
Per arriving claim the arm chooses **pay** (as billed), **pend** (request the chart) or **adjust** (pay one level lower by rule, no chart). A pended claim ends in one of:

| Outcome | What happens | Paid |
|---|---|---|
| Chart returns in time | rules read the chart: supported level L | justified-level price if the read is right; otherwise see *read accuracy* |
| Chart partial or deficient | one follow-up round (as office 2.1), then as above or as expired | |
| Office answers NO_RECORD (never rendered) | nothing to read | 0 (denied): the fraud prevented in full |
| No answer by the wait limit | `EXPIRED_POLICY` | default `deny`; sensitivity `pay_billed` |

## Parameters
| Parameter | Value | Source / status |
|---|---|---|
| Pay-or-pend decision time | on receipt; staff capacity of `PEND_CAP_PER_DAY` pends | **assumption** (a daily cap stands for review staff; swept) |
| Prompt-pay deadline | 30 days from receipt | **assumption**; state and contract clocks vary (to source, issue 9) |
| Wait limit for records | 45 days | **assumption**, borrowed from Medicare ADR's 45 days |
| `EXPIRED_POLICY` | deny | **assumption**; in practice requested claims are denied or recouped when records do not arrive (postpay issue 68). Non-response is not evidence of upcoding |
| Read accuracy | chart rules read the supported level from the generated chart as the postpay rules do; the rate of a wrong read is measured on development seeds and reported, not assumed zero | measured |
| Appeals | a wrongful adjustment or denial is appealed with probability `P_APPEAL` and overturned with certainty; unappealed wrongful loss still counts in WrongfulLoss (the payer cannot count a wrongful denial as saved) | `P_APPEAL` = 0.5, **assumption**; KFF's Medicare Advantage figures (11.5% of denials appealed, 80.7% overturned) are for another market and are not used |

## Staff cost (hours x loaded wage, wages x 1.4 as in score 4.0)
| Item | Value | Status |
|---|---|---|
| Automatic screen of an arriving claim | $0.05 | **assumption** (compute and queue cost) |
| Triage of a pended claim | 5 minutes, analyst | **assumption** (score 4.0 uses 15 minutes per listed provider) |
| Request admin | 10 minutes per pended claim, admin wage | **assumption** (score 4.0: 30 minutes per request round of many charts) |
| Chart review | 15 minutes per chart, coder wage | score 4.0 |
| Copy fee | $3 per chart | derived: score 4.0's $90 per round at 30 charts; commercial plans often pay none (the postpay commercial profile sets $0) |
| Follow-up round | 10 minutes admin + $3 | **assumption** |
| Appeal handling | 45 minutes coder per appealed claim | **assumption** |
| Model dollars | the arm's API cost | measured |

## Abrasion
Weights are claim-level truth: `w(c) = 1` when the billed level is supported (or lower), `0` when the claim is overbilled (a pend of an upcoded claim costs the provider nothing it was not already liable for). This is the claim-level version of score 4.0's provider-level weight, and a claim that was never rendered has `w = 0`.

| Item | Value | Status |
|---|---|---|
| Wrongful pend | $43.84 x w(c) | score 4.0's abrasion per request round |
| Delay | w(c) x paid amount x 18% per year x days past the prompt-pay deadline / 365 | **assumption** (interest on late payment; statutory rates vary, to source) |
| Wrongful adjustment or denial | $200 x w'(c), w'(c) = 1 when paid < justified | **assumption** (provider's appeal effort and goodwill; score 4.0 uses $2,000 per demand, which is a larger action) |

## Reported beside the score, not in it
Share of overbilled dollars prevented; claims pended, adjusted and denied; wrongful pends and wrongful adjustments per 1,000 claims; median and 90th percentile days to payment; expired pends; read errors; dollars from never-rendered claims versus level differences; score divided by the oracle score.

## References every arm is read against
Pay-all (zero by construction); claim edits with no chart (point 3); automatic one-level adjustment of every level 4 and 5 claim from providers above a threshold (point 6, with its wrongful-adjustment cost); the **oracle with triage** (pends exactly the overbilled claims whose prevented dollars exceed their pend cost, an upper bound that reads the answer key).

## Known weaknesses of P1.0
- Wrongful-pend and delay costs are the least sourced terms; the score's ordering of arms must be shown to hold across the sensitivity range before any ranking is claimed.
- Chart in hand means no extrapolation, so prepay's Prevented is exact where postpay's recovery was a lower bound. Compare arms at equal review (same number of charts) before saying prepay is better.
- Providers do not learn: a real provider changes its billing once it is pended often. Not simulated (issue for a later release).
