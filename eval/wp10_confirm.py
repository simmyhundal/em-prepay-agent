"""The one declared confirm of WP1.0 on P-CONFIRM j = 0 to 19 (docs/wp10_confirm_declaration.md), or with --final-dev the final development run on P-DEV j = 50 to 59 (docs/wp10_freeze.md). Real decisions through the real score. Free.
Usage: python eval/wp10_confirm.py [--record]"""
import hashlib
import json
import multiprocessing as mp
import os
import pickle
import sys

import numpy as np
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import claim_stream as cs
import edit_rules
import provider_prior
import score_prepay as sp
import seed_registry as reg
import wp10
import wp10_loop as L
from run_prepay_reference import build

FINAL_DEV = "--final-dev" in sys.argv                      # the final development run on P-DEV j = 50 to 59 (docs/wp10_freeze.md)
CONFIRM = [2001 + 41 * j for j in range(50, 60)] if FINAL_DEV else [2002 + 41 * j for j in range(20)]
POOL, ARMS = ("P-DEV", ("WP1.0-final-dev",)) if FINAL_DEV else ("P-CONFIRM", ("WP1.0", "REF-edits-tuned"))
OUT = os.path.join(ROOT, "experiments", "wp10", "final_dev.json" if FINAL_DEV else "confirm.json")


def one(args):
    seed, rule, rule_np = args
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    prior = provider_prior.CausalPrior(stream)
    X = wp10.claim_features(stream, prior)
    j = wp10.FEATURES.index("n_today_clinician")
    arms = {"wp10": wp10.decisions(stream, office, wp10.pick(stream, rule.predict(X), wp10.CAP_PER_DAY, 0.0)),
            "wp10_noprior": wp10.decisions(stream, office, wp10.pick(stream, rule_np.predict(X), wp10.CAP_PER_DAY, 0.0)),
            "hand_rule_c1": wp10.decisions(stream, office, wp10.pick(stream, X[:, j], wp10.CAP_PER_DAY, 19.5)),
            "edits_tuned": edit_rules.run(stream, by="rendering", daily_max=20, member_max=6), "pay_all": []}
    res = {}
    for name, dec in arms.items():
        scr = name != "pay_all"
        r = sp.score(stream, truth, dec, screened=scr)
        r["sensitivity"] = sp.sensitivity(stream, truth, dec, scr)
        res[name] = r
    return seed, res


def main():
    F = wp10.FEATURES
    rule = L.fit_rule(L.FIT)
    rule_np = L.fit_rule(L.FIT, features=[f for f in F if f != "log_prior"])
    digest = hashlib.sha256(pickle.dumps(rule)).hexdigest()[:16]
    for arm in ARMS:
        reg.check_run("4.2", CONFIRM, arm, "confirm")
    with mp.get_context("spawn").Pool(8) as p:
        per = dict(p.map(one, [(s, rule, rule_np) for s in CONFIRM]))
    sc = lambda arm: np.array([per[s][arm]["score"] for s in CONFIRM])
    out = {"seeds": CONFIRM, "model_sha256_16": digest, "per_seed": per, "summary": {}}
    w, e = sc("wp10"), sc("edits_tuned")
    for arm in ("wp10", "wp10_noprior", "hand_rule_c1", "edits_tuned", "pay_all"):
        v = sc(arm)
        out["summary"][arm] = {"sum": round(float(v.sum())), "median": round(float(np.median(v))), "above_zero": int((v > 0).sum()),
                               "largest_seed_share": round(float(v.max() / v.sum()), 3) if v.sum() > 0 else None}
    d = w - e
    t = stats.ttest_rel(w, e)
    out["primary"] = {"mean_gain_per_seed": round(float(d.mean())), "sum_gain": round(float(d.sum())), "p_one_sided": float(t.pvalue / 2 if t.statistic > 0 else 1 - t.pvalue / 2),
                      "p_two_sided": float(t.pvalue), "seeds_better": int((d > 0).sum()), "pass": bool(d.mean() >= 3000 and t.statistic > 0 and t.pvalue / 2 < 0.05)}
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({"summary": out["summary"], "primary": out["primary"], "model": digest}, indent=1))
    if "--record" in sys.argv:
        if FINAL_DEV:
            reg.record_use("4.2", "P-DEV", "WP1.0-final-dev", "confirm", CONFIRM, "docs/wp10_final_dev.md", "frozen WP1.0 beside the tuned edit and the hand rule; a final development run, not a test", "2026-10-23")
        else:
            reg.record_use("4.2", "P-CONFIRM", "WP1.0", "confirm", CONFIRM, "docs/wp10_confirm.md", "frozen H7 read once against the tuned edit", "2026-10-23")
            reg.record_use("4.2", "P-CONFIRM", "REF-edits-tuned", "confirm", CONFIRM, "docs/wp10_confirm.md", "comparison arm for the WP1.0 confirm", "2026-10-23")


if __name__ == "__main__":
    main()
