"""Reference arms on development seeds (issue 3): pay-all, claim edits (point 3), automatic adjustment (point 6, two variants), the oracle with triage.
Usage: python eval/run_prepay_reference.py [--n 10] [--seeds 2001 2042 ...]   Free; no model calls. Writes experiments/prepay_reference/results.json."""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import claim_stream as cs
import edit_rules
import level_adjust
import prepay_oracle
import score_prepay as sp
import seed_registry as reg

GEN = os.path.join(ROOT, "external", "em-upcoding-agent", "src", "generate_v2.py")
DEV = [2001 + 41 * j for j in range(60)]


def build(seed):
    out, key = os.path.join(ROOT, "data", f"pp_{seed}"), os.path.join(ROOT, "eval", "answer_key", f"pp_{seed}.json")
    if not os.path.exists(os.path.join(out, "remittance.csv")):
        os.makedirs(os.path.dirname(key), exist_ok=True)
        subprocess.run([sys.executable, GEN, out, "--seed", str(seed), "--data-version", "4.2", "--answer-key", key], check=True, capture_output=True)
    return out, key


def arms(stream, office, truth):
    return {"pay_all": [], "edits": edit_rules.run(stream), "auto_all": level_adjust.run_all(stream),
            "auto_provider": level_adjust.run_provider(stream), "oracle": prepay_oracle.run(stream, office, truth)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seeds", type=int, nargs="*")
    a = ap.parse_args()
    seeds = a.seeds or DEV[:a.n]
    for arm in ("REF-edits", "REF-auto_provider"):
        reg.check_run("4.2", seeds, arm, "select")
    results = {}
    for seed in seeds:
        d, key = build(seed)
        stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
        truth = sp.claim_truth(key, stream)
        res = {}
        for name, dec in arms(stream, office, truth).items():
            scr = name != "pay_all"
            r = sp.score(stream, truth, dec, screened=scr)
            r["sensitivity"] = sp.sensitivity(stream, truth, dec, scr)
            res[name] = r
        res["_claims"] = len(stream.claims)
        res["_overbilled_dollars"] = round(sum(stream.by_id[k].paid - v["payable"] for k, v in truth.items() if v["overbilled"]), 2)
        results[seed] = res
        print(seed, {k: res[k]["score"] for k in res if not k.startswith("_")}, flush=True)
    out = os.path.join(ROOT, "experiments", "prepay_reference")
    os.makedirs(out, exist_ok=True)
    json.dump(results, open(os.path.join(out, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
