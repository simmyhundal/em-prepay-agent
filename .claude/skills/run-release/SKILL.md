---
name: run-release
description: Run the full release process of this prepay project (core stories, setting, hypothesis loop, freeze and final dev run, agent parity, true test with the paid agent run, close-out and reflection). Use when the user types /run-release (optionally with "paid cap=N") or asks to run the full release process.
---

Run one full release cycle of this project by following `docs/process.md` and `CLAUDE.md`, in order. Start by reading both and `docs/prepay_plan.md` if it exists, the open milestones (`gh issue list`), `experiments/seed_registry.json`, `docs/decision_log.md`, the latest `docs/releases/` notes and the latest `docs/reflection_*.md`, then say which step the project is at and what you will do next.

Arguments:
- **`paid`** (with an optional `cap=N` in dollars, default 5 for the whole release): Simmy's standing approval to run the paid step (the agent's true test) without asking. Log the estimate in `docs/decision_log.md` before spending, never spend past the cap (stop and say so if the estimate exceeds what is left), keep the per-run caps of the runners, and log the cost afterwards. Without `paid`, stop at the paid run and state the estimate and the cap first.
- **`until-done`** (implied by `paid`): keep going through the steps without stopping to ask, using background agents for long runs, until the release is done or the session limit is reached; if the limit is reached, leave `docs/decision_log.md` and the open issues current so the next session can resume at the right step.
- A step number or issue number (for example `/run-release step 3`) starts there.

Rules that hold throughout:
- The step list, the yardsticks (the previous workflow re-run on the same seeds, zero, the oracle with triage), the seed plan, the control for mechanical gains and the freeze declaration are in `docs/process.md`. Declare before you run; never tune on a test seed. Earlier workflow arms are re-run (free); earlier agent runs are never re-run.
- Work autonomously on everything the process lists as autonomous and log each important event in `docs/decision_log.md`.
- Finish with the close-out (README, figures, notes, tags and releases, registry, log) and the reflection on the deepest flaws of the system, then a short summary of what changed and what is next.
- Write for outside readers (`docs/process.md`, Writing for outside readers): plain lead paragraph, industry term where one exists, a concept page and a glossary row for each project term, linked at first use with a hover title, and a terminology test updated for each new or changed page. Check this before closing out a release.
