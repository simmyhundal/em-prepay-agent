"""Tune the claim edits (prepay point 3) and the provider-level adjustment (point 6) on the development pool (issue 5 setup; spec in docs/prepay_reference_arms.md).
Stage `select`: a threshold grid is scored on P-DEV j = 10 to 19 (role select, arms REF-edits and REF-auto_provider); the setting with the highest summed score wins, with
"never act" (pay-all, zero) a candidate in each grid; the choice is written to experiments/prepay_reference/tuning.json before anything else is read.
Stage `confirm`: the chosen settings are read once on P-DEV j = 20 to 29 (role confirm, arms REF-edits-tuned and REF-auto_provider-tuned), beside pay-all and the oracle.
Usage: python eval/tune_prepay_reference.py select|confirm [--record]    Free; no model calls.   --record writes the use into the seed registry."""
import argparse
import itertools
import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import claim_stream as cs
import edit_rules
import level_adjust
import prepay_oracle
import score_prepay as sp
import seed_registry as reg
from run_prepay_reference import DEV, build

OUT = os.path.join(ROOT, "experiments", "prepay_reference", "tuning.json")
SELECT, CONFIRM = DEV[10:20], DEV[20:30]
EDIT_GRID = [dict(by=b, daily_max=d, member_max=m) for b in ("provider", "rendering") for d in (5, 8, 10, 15, 20, 30, 45, 60, 90) for m in (2, 3, 4, 6, 999)]
AUTO_GRID = [dict(by=b, delta=x, min_n=n) for b in ("provider", "rendering") for x in (0.05, 0.1, 0.15, 0.2, 0.3, 0.4) for n in (20, 100, 300)]
KEY = lambda cfg: json.dumps(cfg, sort_keys=True)


def grid_scores(seed):
    d, key = build(seed)
    stream = cs.Stream(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    out = {"edits": {}, "auto_provider": {}}
    for cfg in EDIT_GRID:
        out["edits"][KEY(cfg)] = sp.score(stream, truth, edit_rules.run(stream, **cfg))["score"]
    for cfg in AUTO_GRID:
        out["auto_provider"][KEY(cfg)] = sp.score(stream, truth, level_adjust.run_provider(stream, **cfg))["score"]
    return seed, out


def read_chosen(seed, chosen):
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    arms = {"pay_all": [], "edits_first_guess": edit_rules.run(stream), "auto_provider_first_guess": level_adjust.run_provider(stream),
            "oracle": prepay_oracle.run(stream, office, truth)}
    for name, run in (("edits", edit_rules.run), ("auto_provider", level_adjust.run_provider)):
        if chosen[name] is not None:
            arms[name + "_tuned"] = run(stream, **chosen[name])
    res = {}
    for name, dec in arms.items():
        r = sp.score(stream, truth, dec, screened=name != "pay_all")
        r["sensitivity"] = sp.sensitivity(stream, truth, dec, name != "pay_all")
        res[name] = r
    res["_overbilled_dollars"] = round(sum(stream.by_id[k].paid - v["payable"] for k, v in truth.items() if v["overbilled"]), 2)
    return seed, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["select", "confirm"])
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    today = "2026-10-23"
    if a.stage == "select":
        for arm in ("REF-edits", "REF-auto_provider"):
            reg.check_run("4.2", SELECT, arm, "select")
        with Pool(8) as p:
            per = dict(p.map(grid_scores, SELECT))
        result = {"seeds": SELECT, "grids": {}}
        for name, grid in (("edits", EDIT_GRID), ("auto_provider", AUTO_GRID)):
            rows = []
            for cfg in grid:
                v = [per[s][name][KEY(cfg)] for s in SELECT]
                rows.append({"config": cfg, "sum": round(sum(v), 2), "per_seed": v, "seeds_above_zero": sum(x > 0 for x in v)})
            best = max(rows, key=lambda r: r["sum"])
            result["grids"][name] = {"rows": rows, "n_configs": len(rows), "chosen": best["config"] if best["sum"] > 0 else None, "best_sum": best["sum"]}
            print(name, "best", best["config"], best["sum"], "above zero in", best["seeds_above_zero"], "of 10; chosen:", result["grids"][name]["chosen"])
        json.dump(result, open(OUT, "w"), indent=1)
        if a.record:
            for arm in ("REF-edits", "REF-auto_provider"):
                reg.record_use("4.2", "P-DEV", arm, "select", SELECT, "docs/prepay_reference_arms.md", "threshold grid scored on j = 10 to 19; choice in experiments/prepay_reference/tuning.json", today)
    else:
        sel = json.load(open(OUT))
        chosen = {k: v["chosen"] for k, v in sel["grids"].items()}
        for arm in ("REF-edits-tuned", "REF-auto_provider-tuned"):
            reg.check_run("4.2", CONFIRM, arm, "confirm")
        with Pool(8) as p:
            per = dict(p.map(__import__("functools").partial(read_chosen, chosen=chosen), CONFIRM))
        sel["confirm"] = {"seeds": CONFIRM, "chosen": chosen, "per_seed": per}
        json.dump(sel, open(OUT, "w"), indent=1)
        for arm in sorted({k for v in per.values() for k in v if not k.startswith("_")}):
            v = [per[s][arm]["score"] for s in CONFIRM]
            print(arm, round(sum(v)), "above zero", sum(x > 0 for x in v))
        if a.record:
            for arm in ("REF-edits-tuned", "REF-auto_provider-tuned"):
                reg.record_use("4.2", "P-DEV", arm, "confirm", CONFIRM, "docs/prepay_reference_arms.md", "the setting chosen on j = 10 to 19, read once on j = 20 to 29", today)


if __name__ == "__main__":
    main()
