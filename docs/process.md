# The release process

[Back to the README](../README.md) · [decision log](decision_log.md) · [seed roles](seeds.md) · [versions](versioning.md)

How a release of this project is run, so it can continue with little input from Simmy. Written 2026-10-22 from the v4.0 to v5.1 cycle. To run the whole cycle in a new session, use the command **`/run-release`** (the skill in `.claude/skills/run-release/SKILL.md` reads this page and CLAUDE.md and follows it).

The command **`/run-release`** takes an argument: `/run-release paid cap=5` grants Simmy's standing approval to run the paid step without stopping, up to $5 for the release (any cap), and to keep going until the release is done or the session limit is reached; without `paid` the run stops at the paid run to ask. See the skill.

A release Y pairs a data version (from the pinned generator, starting at 4.2), a prepay workflow, a prepay agent and a score version that is fixed before the work starts. Version names and the first release are set in `docs/prepay_plan.md` (to write). Copied from the postpay repository's process on 2026-10-23; wherever it names S4.x, W4.x, A5.x or postpay results, read the prepay equivalents.

## The steps

**1. Core stories.** File issues in the new release's milestone that fix the shortcomings of the last release, from what its test showed and hypotheses about the causes. Before any work, write down:
- *The yardsticks.* The last release's workflow on the same new test seeds (free to run), the do-nothing baseline (zero), and the **oracle**: the best conceivable score under the same score version, with the same costs a tuned arm pays, **triage included** (it lists, and so triages, the providers it pursues). **Stress-test every yardstick when it is built** (a README table will quote it for months): write down the rules it works inside and what they exclude; print its breakdown (prevented dollars, staff cost, abrasion, claims pended, by kind); use at least 20 random samples per estimate, because choosing the best of noisy estimates biases a ceiling upward; check that no arm beats it and that every cost an arm pays is charged to it too; and have a second reviewer read it before it is published. Report "score divided by oracle score" with the oracle's definition and seeds (a ceiling-benchmarks page, as in the postpay repository). The oracle uses the answer key, so it is an upper bound.
- *The seed plan.* Allocate a development pool, a confirm pool and a **new, unrun test pool**, keep one reserved pool untouched, and record their roles in the [seed registry](seeds.md) (`experiments/seed_registry.json`). Do not reuse a test pool unless it is declared a second look.
- *The power plan.* Estimate how many seeds a plausible effect needs (the postpay repository's paired per-seed differences had a spread of about $800 to $1,300, so 20 to 60 seeds detect only large effects and about 100 seeds an effect of about $300 per seed; measure the spread again for prepay) and size the pools for it. A single pre-declared confirmatory test on unused seeds avoids most of the multiple-comparison penalty. **Re-measure the spread on the first 20 seeds of any new data version before fixing the sizes.**
- *The order and the money.* State each story's dependencies and the order they are worked in, and list every paid step with its estimate, so the release's total is known in step 1 and one cap can be set for the skill run (`paid cap=N`).

**2. Setting (optional).** Decide the score and data versions for the release before the hypothesis work, when the last release exposed a deficiency in them. Re-score the frozen references (the last workflow and agent) on the new score and data and publish that table first, so the new numbers have something to compare with. Keep the old score and data versions frozen: a new version is a new module. **When a data version adds a mechanism, update the oracle, the scorer and the truth schema in this step**, and stress-test the oracle again. **A new score version, or a change to any score parameter, is decided with Simmy before the loop starts** (ask first). An assumptions track runs beside the loop: each cycle, source at least one unverified parameter (the copy fee, minutes per task, dollars per provider), and the market research track (milestone "Payer stock-price drivers") feeds this step.

**3. Work the core stories.** Develop hypotheses on the workflow arm (free), one change each against the current best, on the development pool. Rules:
- Choose any parameter on the *select* batches; test once on a *confirm* batch declared in advance; never adjust after looking.
- Count every hypothesis tried and use the Bonferroni bar (0.05 divided by the number tried); report a result below the bar as a result and anything else as a lead.
- **Run the control for any mechanical gain.** A shorter list, fewer charts or no asks are acceptable ways to raise the score, but the same saving applied to the baseline (for example H8 with a 4-provider list) must be run, so the gain is split into what is mechanical and what is better asking.
- Write the result of each hypothesis in the loop's docs pages, comment on the issue, and merge docs and result files.

**4. Freeze and the final development run.** Write a freeze declaration (the postpay repository's `docs/w41_freeze.md` is the template) before the run: what is frozen, the seeds, the arms, the comparisons and the pass criterion ("marked improvement": a stated dollar gain per seed and a p-value). Then run the frozen workflow, **the previous release's workflow arm and the same-list control, all freshly (they are free)**, on the previous release's test seeds. Those seeds were burned by the last release's test, so this is the *final development run*, not a test. If the frozen workflow misses the criterion, reopen the core stories (a reopen costs nothing here because no fresh seed was spent).

**5. Agent at parity.** Build the agent arm to mirror the frozen workflow in its tools. Report parity from a scripted agent that follows the advice, on development seeds only (same asks, same calls, same score, as match rates), and a cost estimate for the paid run from the previous agent's recorded usage.

**6. The true test on fresh seeds.** Generate the release's test pool (ten seeds nobody has run; the registry's reserved pool), then run on it **once**: the frozen workflow, the previous release's workflow and the control (free), and the agent (the only step that costs money: state the estimate and the cap, get Simmy's approval or use the standing approval of `/run-release paid`, then run once). Compare the workflow with the previous workflow and the control, and the agent with the workflow. If the paid cap allows, repeat the agent on a few seeds to size its run-to-run noise; otherwise say in the result page that it is unmeasured. The previous *agent* is never re-run: it is compared indirectly, through the previous workflow that was run on the same seeds (the project is price sensitive). Earlier *workflow* arms are always re-run on new seeds; earlier *agent* runs never are. After the test the pool is burned and a new reserved pool is allocated in the next release's step 1.

**7. Close out and reflect.** Update the README table and summary, the figures (progression slide, workflow and agent figures, waterfall), `docs/versioning.md`, the results pages and the seed registry; write the release notes; **tag and publish the GitHub releases**; clean up the milestone and issues; record in the decision log; note what each hypothesis taught; apply [Writing for outside readers](#writing-for-outside-readers) to every page the release added or changed (new terms get concept pages). Then a point of deeper reflection: **what are the deepest flaws in our current system?** Write the answer in `docs/reflection_<release>.md` (the data, the score and its assumptions, the statistics and seed use, the arms, the process, the product): what is by construction, what is unverified, what a sceptic would attack, and what we are not measuring. These flaws seed the next release's step 1 (file an issue for each one worth fixing). Step 7 of one cycle is the start of the next.

**The close-out checklist** (every item is checked before the release is tagged):
- The README is under its cap (`tests/test_readme_sync.py`), every table row uses one yardstick, and every table column has a row in the glossary (`tests/test_readme_columns.py`). Name check: for each new column write one plain sentence; if the label alone would mislead, rename it.
- Every figure was rendered and looked at in the browser pane (spacing, clipped text, a zero line inside the drawing); a figure's numbers come from the results files, not from typing.
- The decision log, release notes, seed registry, `docs/seeds.md` and issues are current, and the milestone is closed with its leftovers moved on.
- The outside-reader pass (below) was run and its findings fixed or filed.

## Writing for outside readers

Decided 2026-10-23. Subject-matter experts (payment integrity, SIU, health plans) read these pages without having built the project, so every page a release adds or changes follows these rules. Step 7 checks them.

1. **Open with what the page is.** One paragraph a newcomer can follow: what question the page answers and what it assumes. Put version tags and issue numbers after the plain description, not in the heading.
2. **Use the industry term when there is one** (workflow versus agent, triage, extrapolation, lower confidence limit) and define it at first use. Invent a project term only when no industry term fits, and give it a plain name that says what it does ("break-even rule", not "demand floor").
3. **One concept, one page.** Every project term gets a short page in `docs/concepts/` (to create) with *what it means, why it exists, an example, where to find it*, and a row in the glossary's Project terms table that also lists the old or code name.
4. **Link at first use** to the concept page with a hover title (`[term](concepts/x.md "one-line meaning")`; GitHub shows link titles on hover). Code names (`hybrid_review`, `near_miss`) stay in code spans and are never the only name for an idea.
5. **Say what a number is made of.** A dollar figure names its unit (per seed, summed over ten seeds), its source version, and the assumption that moves it most.
6. **Enforce it.** Add each new or changed page to `OUTSIDE_PAGES` in `tests/test_concepts.py` and each retired term to its `OLD` list; the test fails if an old term appears outside code or a concept link is missing. The README stays under its length cap.

## Running without stopping (`/run-release paid` or `until-done`)

Added 2026-10-23, after a run ended its turn to wait for background jobs and handed the release back to Simmy. The rule: **a release run ends only when the release is done, the session limit or the spend cap is reached, or an "ask first" item (below) is next. Waiting is never a reason to stop, and neither is a prerequisite that is not ready yet.**

1. **Keep a pin list.** The task list always holds every remaining step of the process, and any item blocked on something (a background run, a build, a PR check, a step that needs an earlier step's output) stays on it as pending with its blocker written in the item ("waiting for H24 to Z: then freeze"). Work the next unblocked item; return to a pinned one when its blocker clears. Write the same list into `docs/decision_log.md` or the release plan page when the session might end, so another session can resume.
2. **Never end the turn to wait.** Start long free runs in the background, then do other work: docs, tests, concept pages, the agent build, the next hypothesis, the close-out drafts. When nothing independent is left, wait inside the turn with a blocking command (`until <done>; do sleep 20; done` run in the foreground up to the shell's time limit, then again) or a Monitor on the output file. A monitor expiring is not a stopping point: check the output, re-arm, continue.
3. **Do not call the wrap-up box until the run is finished or blocked on an "ask first" item.** A recap with nothing for Simmy to decide is an interim status, not a stop: send it as ordinary text between tool calls if it is useful, and keep working.
4. **Order of operations is not a blocker.** If step N+1 needs step N's output, do the parts of N+1 that do not (code, tests, docs, estimates), pin the rest, and resume it when N lands. Registry entries, decision-log rows and issue comments are written as the events happen, not saved for the end.
5. **Decide, log, move on.** A choice the process lists as autonomous is made by the run, recorded in the decision log with the reason, and Simmy reviews it afterwards. Ask only for the "ask first" items: a paid run beyond the standing approval or the cap, deleting a repository or an unmerged branch, anything Simmy asked to hold.
6. **If the session limit nears,** stop starting new long runs, commit and push what exists, update the pin list in the decision log with the exact next command for each pinned item, and then end.

## Before a merge, a tag or a release

Carried over from the postpay repository (2026-10-25).

1. **Start every branch from a fresh `origin/main`** (`git fetch`, then `git checkout -b NAME origin/main`) and rebase before merging.
2. **Run the fast checks before every merge:** `sh tests/run_fast.sh` (all tests, under a minute, no model calls). The full pass with a paid agent run happens once per release before the tag.
3. **One fact, one home.** Each kind of page owns one kind of content (the doc map in `CLAUDE.md`); a number in prose either sits in a generated block or links to the page that generates it.
4. **The outside-reader pass.** Before a tag, start a fresh in-session sub-agent (no extra API calls, no spend) with no context beyond the README and the pages it links to, and ask it to list every term, number or step it cannot follow and every claim it cannot trace to a page. Fix what it finds or file it.
5. **Do not sync with the postpay repository, or any sibling, without Simmy's permission.** Say in one line that a change was not mirrored.
6. **Record events as they happen** in the decision log.
7. **Data is built in the postpay repository** and pinned here (`GENERATOR_PIN`). When a data version is built sealed there (docs/process.md of that repository, "Sealed data design"), read only its public contract (build command, files and fields, answer-key schema, data card).

## Who decides what

Decided 2026-10-22 so work can continue when Simmy is busy.

**Autonomous (do it, then log it in [decision_log.md](decision_log.md)):** free runs and analysis; docs, notes and issues; opening and merging pull requests when the tests pass; **merging edits that touch frozen-version code paths** (refactors and new options, as long as the frozen version still reproduces: its tests and a replay pass); **tagging and publishing GitHub releases**; milestone and issue cleanup; building the next arm.

**Ask first:** **a new score version or a change to a score parameter; the scope of a new data version;** a **paid run** (state the estimate and the cap first), unless the command was given with `paid` (then spend up to its cap and log the estimate and cost); deleting a repository or a branch other than a merged branch; anything Simmy has asked to hold.

**Never:** changing a tagged version's results (a frozen version is reproduced by hash and by replay; behaviour changes go behind a new version flag, as CLAUDE.md says), reading the answer key in an arm or its tools, tuning on a test seed and calling it held out, generating or running the reserved pool before the freeze, printing or committing the key in `.env`.

A spend cap applies per release (the agent run's batch cap is the guide; the v5.1 run cost $1.24). If a decision is not covered here, take the cautious option and put it in the log for review.

## What each step produces
Core stories: issues, the yardstick table, the seed and power plans. Setting: re-scored references. Loop: per-hypothesis docs and result files. Freeze: the declaration and the result page. Parity: the parity numbers and the estimate. Paid run: the result page and the cost. Close-out: the README, figures, release notes, tags, the registry and the log.
