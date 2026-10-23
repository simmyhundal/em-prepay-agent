"""The seed registry (issue 176): which seeds were fitted, selected, confirmed or tested on, per arm and per data version.

The registry is `experiments/seed_registry.json`; `docs/seeds.md` is generated from it (`eval/seed_registry_report.py`).
A seed number alone means nothing: data 4.0 seed 1515 and data 2.2 seed 1515 are different datasets, so every lookup is by (data version, seed).

Roles: fit (parameters estimated), select (a setting chosen), confirm (a hold-out read once for a decision declared in advance), test (a fresh set read once for a frozen version).
Free; no model calls. Reading the registry never runs anything; `check_run` only raises."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "experiments", "seed_registry.json")
ROLES = ("fit", "select", "confirm", "test")
STATUSES = ("fresh", "reserved", "in_use", "burned")
KINDS = ("development", "test")


class SeedRegistryError(Exception):
    """A run would break the seed rules (see check_run)."""


def load(path=None):
    with open(path or PATH) as f:
        return json.load(f)


def canonical(reg, arm):
    """The arm name the registry uses (W4.0 is H8; W4.1 is H23 at N = 4)."""
    return reg.get("arm_aliases", {}).get(arm, arm)


def line(arm):
    """'agent' for A3.x/A5.x and v3.x, else 'workflow' (workflow versions, loop hypotheses H*, controls)."""
    return "agent" if re.match(r"^(A\d|v3\.)", arm) else "workflow"


def pool_seeds(pool):
    return set(pool["seeds"])


def find_pools(reg, data, seeds):
    """{pool id: (pool, the requested seeds that fall in it)}; seeds in no pool are returned under None."""
    out, missing = {}, []
    for s in seeds:
        hit = [p for p in reg["pools"] if str(p["data_version"]) == str(data) and int(s) in pool_seeds(p)]
        if not hit:
            missing.append(int(s))
            continue
        p = hit[0]
        out.setdefault(p["id"], (p, set()))[1].add(int(s))
    return out, missing


def _use_seeds(pool, use):
    return set(use.get("seeds", pool["seeds"]))


def describe(data, seed, reg=None):
    """The roles recorded for one seed: {'pool', 'kind', 'status', 'uses': [(arm, role, done, second_use)]}, or None if no pool has it."""
    reg = reg or load()
    found, _ = find_pools(reg, data, [seed])
    if not found:
        return None
    pool, _s = next(iter(found.values()))
    uses = [(u["arm"], u["role"], u.get("done", True), bool(u.get("second_use"))) for u in pool["uses"] if int(seed) in _use_seeds(pool, u)]
    return {"pool": pool["id"], "kind": pool["kind"], "status": pool["status"], "uses": uses}


def check_development(data, seeds, reg=None):
    """For the development loop: raise when a seed is in a reserved or fresh pool, or in a test pool. Seeds in no pool pass (the loop's own assertion bounds them)."""
    reg = reg or load()
    found, _missing = find_pools(reg, data, seeds)
    for pid, (pool, hit) in found.items():
        if pool["status"] in ("reserved", "fresh") or pool["kind"] == "test":
            raise SeedRegistryError(f"seeds {sorted(hit)} are in pool {pid} (status {pool['status']}, kind {pool['kind']}): the development loop may not run them")


def check_run(data, seeds, arm, role, second_use=False, reg=None):
    """Raise SeedRegistryError when running `arm` on `seeds` of `data` in `role` breaks a rule.

    (a) a reserved pool is never run; a fresh pool only as a test; a test pool is never fitted or selected on.
    (b) an arm that fitted or selected on a seed cannot confirm or test on it (and the reverse: a seed already read as hold-out cannot then be fitted or selected on).
    (c) a test on a pool that already has a first test by the same line (workflow or agent) needs second_use=True, unless this arm is already recorded there with the same flag (a replay)."""
    reg = reg or load()
    if role not in ROLES:
        raise SeedRegistryError(f"unknown role {role!r}; use one of {ROLES}")
    arm = canonical(reg, arm)
    seeds = [int(s) for s in seeds]
    found, missing = find_pools(reg, data, seeds)
    if missing:
        raise SeedRegistryError(f"seeds {missing} of data {data} are in no pool of the registry; register them in experiments/seed_registry.json first")
    for pid, (pool, hit) in found.items():
        if pool["status"] == "reserved":
            raise SeedRegistryError(f"pool {pid} is reserved (never generated, never run): {pool['status_note']}")
        if pool["status"] == "fresh" and role != "test":
            raise SeedRegistryError(f"pool {pid} is fresh: it can only be used as a test, not as {role}")
        if pool["kind"] == "test" and role in ("fit", "select"):
            raise SeedRegistryError(f"pool {pid} is a test pool: {arm} cannot {role} on it")
        for u in pool["uses"]:
            if canonical(reg, u["arm"]) != arm or not u.get("done", True):
                continue
            overlap = _use_seeds(pool, u) & hit
            if not overlap:
                continue
            if role in ("confirm", "test") and u["role"] in ("fit", "select"):
                raise SeedRegistryError(f"{arm} already did '{u['role']}' on seeds {sorted(overlap)} of pool {pid}; a hold-out cannot be a seed the arm fitted or selected on")
            if role in ("fit", "select") and u["role"] in ("confirm", "test"):
                raise SeedRegistryError(f"{arm} was already read as '{u['role']}' on seeds {sorted(overlap)} of pool {pid}; it cannot then {role} on them")
        if role == "test":
            mine = [u for u in pool["uses"] if canonical(reg, u["arm"]) == arm and u["role"] == "test"]
            if mine:  # an arm recorded as tested here may be re-run (a replay), but only as the use the registry records
                if bool(mine[0].get("second_use")) != bool(second_use):
                    raise SeedRegistryError(f"{arm} is recorded on pool {pid} with second_use={bool(mine[0].get('second_use'))}, but this run says second_use={bool(second_use)}")
                continue
            prior = [u for u in pool["uses"] if u["role"] == "test" and u.get("done", True) and not u.get("second_use") and line(canonical(reg, u["arm"])) == line(arm)]
            if prior and not second_use:
                raise SeedRegistryError(f"pool {pid} already had a first test by the {line(arm)} line ({', '.join(u['arm'] for u in prior)}); {arm} on it is a second use: pass second_use=True and record it in the registry")


def ranges(seeds):
    """Seeds as arithmetic runs: '1515 to 2424 step 101; 3000 to 3189 step 21'."""
    s = sorted(seeds)
    runs, i = [], 0
    while i < len(s):
        j = i
        if i + 1 < len(s):
            d = s[i + 1] - s[i]
            j = i + 1
            while j + 1 < len(s) and s[j + 1] - s[j] == d:
                j += 1
        if j == i:
            runs.append(str(s[i]))
        elif j == i + 1:
            runs.append(f"{s[i]}, {s[j]}")
        else:
            runs.append(f"{s[i]} to {s[j]}" + (f" step {d}" if d != 1 else ""))
        i = j + 1
    return "; ".join(runs)
