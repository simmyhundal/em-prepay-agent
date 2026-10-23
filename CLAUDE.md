# CLAUDE.md: start here

Proof of concept for **prepay E/M upcoding prevention** on **synthetic** Medicare-style claims, for payment integrity (PI) teams. For each arriving claim the system chooses: **pay, pend and request records, or pay at a lower level by rule** ("prepay point 4": pend and request records). It is the sibling of [em-upcoding-agent](https://github.com/simmyhundal/em-upcoding-agent) (postpay: audit after payment), which this repository was copied from (see `LINEAGE.md`). Data comes from that repository's **data 4.2** generator, pinned in `GENERATOR_PIN` and fetched by `tools/get_generator.sh` into `external/` (gitignored). A change the prepay work needs in the generator goes into the postpay repository as a new data version, never as a fork here.

The plan is in the postpay repository: `docs/prepay_discovery.md` (points 0 to 6, the design question, the draft score, open questions for the customer) and `docs/prepay_copylist.md` (what to copy, adapt, build). Read them, then this file. Status: nothing built yet beyond the copied process and seed-registry code.

## The designs (to build, side by side)
- **Workflow:** code fixes the order: provider score as a prior, learned pend-or-pay rule, request the chart, rules decide pay, adjust or deny. API-free.
- **Agent:** a model chooses tools within caps and gets the same rule as advice.
- **Reference arms:** pay-all (zero), claim-edit rules with no chart (prepay point 3), automatic one-level adjustment (point 6), the oracle (answer key; pays staff cost like a tuned arm).

## Score (draft, to become score P1.0)
Overpayment prevented minus staff cost minus abrasion. Abrasion = wrongful pends, wrongful adjustments or denials, days of delay past the prompt-pay deadline, appeals overturned. Every parameter is an assumption with a source or a sensitivity. Score in net dollars, summed over ten seeds. Never edit a score version once used; a new score is a new module.

## Rules that matter
- **Answer key is eval-only** (`eval/answer_key/`, gitignored). Never put true levels, rates or fraud kinds in anything an arm or model sees; tests enforce it.
- **Money and keys.** No paid run without the user's OK and an estimate with a cap first, unless `/run-release paid cap=N` was given. The key is in `.env` (gitignored): never print, log, commit or ask for it. Workflow arms stay API-free.
- **Be honest.** Say what is simulated and what is easier by construction (here: the chart is in hand before payment, so no extrapolation is needed; compare arms at equal review). Report results as what the seeds show; one seed carrying a total is a finding.
- **Seeds.** `experiments/seed_registry.json` and `src/seed_registry.py` (roles: fit, select, confirm, test, burned, fresh, reserved) decide what a seed may be used for. Declare pools in the registry before any run. Pools are keyed by data version and seed. Tune only on development seeds; test once on fresh seeds.
- **Release process** is `docs/process.md`; run it with `/run-release`. Autonomous: free runs, docs, merging PRs when tests pass, tagging and publishing releases; log important events in `docs/decision_log.md`. Ask first: paid runs, deleting a repository or an unmerged branch. Earlier workflow arms are re-run on new seeds; earlier agent runs never.
- **Never edit a frozen baseline.** Behaviour changes go behind a version flag.
- **Work through issues** in milestones; `Closes #N` on its own line per issue. End commits with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- **No letters or findings are generated** (no denial or demand letters); a pend notice text is out of scope until legal review.
- README is a short front door, 7,000 characters at most (a test enforces it once the README sync test is adapted); put detail in `docs/`.

## Domain facts
E/M level (99212 to 99215) comes from medical decision making or total time. A pended claim waits on the provider's records; prompt-pay clocks vary by state and contract (parameters, not facts). Medicare ADR (45 days, signature rules) is the postpay analogue; commercial clocks are to be sourced.

## Commands
```bash
tools/get_generator.sh                  # fetch the pinned generators into external/
for t in tests/test_*.py; do python3 $t >/dev/null 2>&1 && echo ok $t || echo FAIL $t; done
```

## Gotchas
- macOS `sed -i` needs `sed -i ''`; the shell resets its working directory between calls (use absolute paths); `python3 -I` ignores numpy.
- Tests copied from the postpay repository that depend on its files were left out (see `LINEAGE.md`); adapt them with the first seed pools.
