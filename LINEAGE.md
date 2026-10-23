# Lineage

Created 2026-10-23 from [simmyhundal/em-upcoding-agent](https://github.com/simmyhundal/em-upcoding-agent) at commit `065c4f1` on `main`.

Plan: prepay point 4 (pend and request records), on data 4.2. Group 1 of the copy-list was copied as-is (license, release process, skill, seed registry code, glossary, CLAUDE.md conventions). The seed registry starts empty. `CLAUDE.md`, `docs/process.md`, `docs/glossary.md` and the skill still describe the postpay product and need rewriting. The generators (`src/generate_v2.py`, `generate_v4.py`, `generate_v42.py`) are not copied: this repository will depend on the postpay repository at a pinned commit. Groups 2 to 4 of the copy-list are not done.

Not yet working here, so left out: `tests/test_readme_sync.py`, `tests/test_seed_registry.py`, `eval/seed_registry_report.py` and `docs/seeds.md` (they depend on postpay-only files); adapt and add them with the first pools.

Update 2026-10-23: `CLAUDE.md`, `docs/process.md`, `docs/glossary.md` and the skill were rewritten for prepay. The generator dependency is `GENERATOR_PIN` plus `tools/get_generator.sh` (checked: a D4.2 dataset of 216 providers builds from the pinned commit).

Update 2026-10-23 (issue 4): `tests/test_readme_sync.py` (7,000-character cap, no milestone headings, links resolve; the figure tests were dropped because there are no figures yet), `tests/test_seed_registry.py`, `eval/seed_registry_report.py` and `docs/seeds.md` were adapted and restored. The registry code gained `plan_use` and `record_use`; the agent line now matches `AP1.x`.
