# Prepay plan: pend and request records

[Back to the README](../README.md) · [score P1.0](score_prepay.md) · [process](process.md) · discovery note and copy-list: in the [postpay repository](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_discovery.md)

Spec for the first release, written 2026-10-23. Read the discovery note first (prepay points 0 to 6, why point 4, open questions for the customer).

## Names
Release P1 = data 4.2 (pinned, `GENERATOR_PIN`), score P1.0, workflow **WP1.0**, agent **AP1.0**. Later releases share the minor (P1.1, ...). Data changes needed here become a data version in the postpay repository.

## The problem as the code sees it
A stream of claims from one dataset (216 providers, a year of claims) arrives in order of receipt date. At each claim the arm sees: the claim, the provider's history **up to that date**, its own budget. It chooses pay, pend or adjust ([score P1.0](score_prepay.md)). A pended claim is resolved after the simulated office answers.

## What data 4.2 already has and what the stream layer adds
- Has: claims with dates and lines, providers, per-claim justified level (`justified_cpt_by_claim` in the answer key), phantom (never rendered) claims with `fraud_claims`, an office that returns charts or `NO_RECORD`, claims lag.
- Adds (new code, `src/claim_stream.py`): the arrival order, a receipt date per claim, the causal history view (nothing after the claim's receipt date), the prompt-pay deadline, the daily pend cap, and the office's per-claim response delay in days (office 4.2 answers at provider level today).
- Causality is tested: a claim's features never use rows dated after it; a test shuffles later rows and requires identical decisions.

## Arms, in order
1. **Pay-all**: zero.
2. **Claim edits** (point 3): rules on the claim and history only, no chart.
3. **Automatic adjustment** (point 6): one level down for flagged level 4 and 5 claims; competitor with its own wrongful-adjustment cost.
4. **Oracle with triage**: upper bound from the answer key.
5. **WP1.0**: provider prior from the screen (`eb_upper_t`, updated as claims arrive), learned pend-or-pay rule, rules read the returned chart. API-free.
6. **AP1.0**: a model chooses tools (`next_claim`, `provider_history`, `pend`, `read_chart`, `pay`, `adjust`) within caps; advice from WP1.0 inside tool results. Paid; only after WP1.0 is frozen.

## Process
The [release process](process.md) applies unchanged: core stories and yardsticks first; seed pools declared in the registry before any run; development batches for the loop; one pre-declared confirm; freeze declaration; final development run; true test once on a fresh pool; the agent's paid run needs an estimate and Simmy's approval; close-out with a reflection. Seeds are keyed by data version 4.2. The postpay pools for 4.2 (development `1001 + 37j`, confirm `1002 + 37j`, test `4700 + 37j`, reserved `5100 + 37j`) were declared there; this repository uses fresh pools of its own, declared here first (issue 4) so a postpay decision cannot burn them.

## Questions the data cannot answer
The open questions for the customer are in the discovery note. The ones that change the score most: how long a claim can wait, what share of pends are appealed and overturned, and who pays for the chart. Until answered, P1.0's values are assumptions with sensitivities.

## Not in release P1
Provider-level prepay status (point 5), providers that change behaviour after being pended, commercial contract variation, real payer data, any letter or notice text.

## Learnings carried over from the postpay repository (2026-10-25)
What the postpay release 4.2 and 5.2 taught that applies here; each is a design rule for the next prepay version, not a result.
1. **A signal separable by construction proves little.** The postpay volume lane reached 60% of its oracle on a signal the generator made perfectly clean (busiest honest day 26 visits, least busy impossible-days provider 33). Prepay's claim edit on visits per day (`src/edit_rules.py`, `daily_max`) is the same kind of rule; before trusting a prepay result on it, test it on data where honest and suspicious volume overlap (postpay issue 197) and report how many honest claims it pends.
2. **Count records not provided, and sample inside a stratum.** A pended claim the office has no record of is an overpayment prevented, not an unknown; where a signal defines a slice of claims, sample inside that slice and extrapolate to it only (`recovery_stratified` in the postpay repository).
3. **Weight abrasion by the provider's total true rate**, including claims for visits that never happened, so a provider whose only fault is phantom visits is not treated as honest.
4. **Share code between the workflow and the agent** (the postpay lane is one module both call), so tool parity cannot drift; call the scripted check "tool and workflow parity", since it tests the tools and not the model.
5. **Stress-test the oracle** (`eval/prepay_oracle.py`): print its breakdown, use 20 or more samples, let it pursue any claim that pays, and charge it every cost an arm pays. A first postpay oracle was far too low (82% of it reached, 60% on the rebuilt one).
6. **People sit at both ends.** Prepay's pend-and-release has a person at the release step; the postpay evaluation modes (stage and human-gate parameters, issue 207 there) map to it: screen only, records only, full run, and a gate that vetoes a fraction of pends or delays release.
7. **Keep the one-seed-carries-the-mean discipline**: report the median and the count of seeds above zero before the mean.
8. **Say what each README number is made of** (unit, version, the assumption that moves it most), and keep one yardstick per table.

