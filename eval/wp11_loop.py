"""The WP1.1 hypothesis loop on P-DEV2 select j = 0 to 19 (plan: docs/wp11_plan.md). Real decisions through the real score P1.0 and its nine-cell cost grid.
Usage: python eval/wp11_loop.py loop      (writes experiments/wp11/loop.json)
Also holds FROZEN (the declared WP1.1 settings, filled in at the freeze) and frozen_rule()."""
import json
import multiprocessing as mp
import os
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
import wp10_loop as L10
from run_prepay_reference import DEV, build

DEV2 = [8001 + 41 * j for j in range(60)]
SEL, CONF, FINAL = DEV2[0:20], DEV2[20:40], DEV2[40:60]
FIT10, FIT20 = DEV[30:40], DEV[30:50]
OUT = os.path.join(ROOT, "experiments", "wp11")
FROZEN = {"fit": "FIT10", "model": {}, "floor": 15.0, "cap": wp10.CAP_PER_DAY}      # WP1.1 as chosen in the loop (docs/wp11_loop.md); frozen by docs/wp11_freeze.md


def make_rule(fit_seeds, **kw):
    return L10.fit_rule(fit_seeds, **kw)


def frozen_rule():
    return make_rule(FIT20 if FROZEN["fit"] == "FIT20" else FIT10, **FROZEN["model"])


def seed_eval(args):
    seed, rules, cands = args
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    prior = provider_prior.CausalPrior(stream)
    X = wp10.claim_features(stream, prior)
    preds = {k: r.predict(X) for k, r in rules.items()}
    j = wp10.FEATURES.index("n_today_clinician")
    arms = {"pay_all": [], "edits_tuned": edit_rules.run(stream, by="rendering", daily_max=20, member_max=6),
            "hand_rule_c1": wp10.decisions(stream, office, wp10.pick(stream, X[:, j], wp10.CAP_PER_DAY, 19.5))}
    for name, (rname, floor, cap) in cands.items():
        arms[name] = wp10.decisions(stream, office, wp10.pick(stream, preds[rname], cap, floor))
    res = {}
    for name, dec in arms.items():
        r = sp.score(stream, truth, dec, screened=name != "pay_all")
        r["sensitivity"] = sp.sensitivity(stream, truth, dec, name != "pay_all")
        res[name] = {k: r[k] for k in ("score", "pended", "denied", "wrongful_pends", "wrongful_adjustments", "prevented", "staff", "abrasion", "fraud_dollars_prevented",
                                      "share_overbilled_prevented", "median_days_to_pay", "sensitivity")}
    return seed, res


def run_seeds(seeds, rules, cands):
    with mp.get_context("spawn").Pool(8) as p:
        return dict(p.map(seed_eval, [(s, rules, cands) for s in seeds]))


def summarize(per, seeds, names, vs="edits_tuned"):
    cells = list(per[seeds[0]]["pay_all"]["sensitivity"])
    out = {}
    for n in names:
        v = np.array([per[s][n]["score"] for s in seeds])
        e = np.array([per[s][vs]["score"] for s in seeds])
        grid = {c: round(sum(per[s][n]["sensitivity"][c] - per[s][vs]["sensitivity"][c] for s in seeds)) for c in cells}
        d = v - e
        out[n] = {"sum": round(float(v.sum())), "median": round(float(np.median(v))), "above_zero": int((v > 0).sum()), "gain_vs_edit_per_seed": round(float(d.mean())),
                  "p_one_sided": float(stats.ttest_rel(v, e).pvalue / 2) if np.any(d != 0) and d.mean() > 0 else 1.0, "seeds_better": int((d > 0).sum()),
                  "mean_gain_over_nine_cells_per_seed": round(float(np.mean(list(grid.values()))) / len(seeds)), "worst_cell_gain_per_seed": round(min(grid.values()) / len(seeds)),
                  "cell_gains_sum": grid, "largest_seed_share": round(float(v.max() / v.sum()), 3) if v.sum() > 0 else None}
    return out


def loop():
    reg.check_run("4.2", SEL, "WP1.1", "select")
    reg.check_run("4.2", FIT20, "WP1.1", "fit")
    rules = {"base10": make_rule(FIT10), "fit20": make_rule(FIT20), "big10": make_rule(FIT10, max_depth=6, max_iter=300)}
    cands = {"WP1.0": ("base10", 0.0, 10), "H11a_floor15": ("base10", 15.0, 10), "H11b_floor30": ("base10", 30.0, 10), "H12_fit20": ("fit20", 0.0, 10), "H13_big": ("big10", 0.0, 10)}
    per = run_seeds(SEL, rules, cands)
    names = ["pay_all", "edits_tuned", "hand_rule_c1"] + list(cands)
    summ = summarize(per, SEL, names)
    os.makedirs(OUT, exist_ok=True)
    json.dump({"seeds": SEL, "candidates": {k: list(v) for k, v in cands.items()}, "summary": summ, "per_seed": per}, open(os.path.join(OUT, "loop.json"), "w"), indent=1)
    if "--record" in sys.argv:
        reg.record_use("4.2", "P-DEV2", "WP1.1", "select", SEL, "docs/wp11_loop.md", "H11 to H13 scored on j = 0 to 19", "2026-10-23")
        reg.record_use("4.2", "P-DEV", "WP1.1", "fit", FIT20, "docs/wp11_loop.md", "rules fitted on j = 30 to 49 (labels from the office only)", "2026-10-23")
    for n in names:
        s = summ[n]
        print(f"{n:16s} sum {s['sum']:>8} >0 {s['above_zero']:>2} gain/seed {s['gain_vs_edit_per_seed']:>6} p {s['p_one_sided']:.3g} nine-cell mean {s['mean_gain_over_nine_cells_per_seed']:>6} worst {s['worst_cell_gain_per_seed']:>6}")


def read(seeds, tag, pool, arm, record, reference):
    """Confirm or final development run: the frozen WP1.1 beside WP1.0 (floor 0), the tuned edit, the hand rule and pay-all. One read; writes experiments/wp11/<tag>.json."""
    reg.check_run("4.2", seeds, arm, "confirm")
    rule = frozen_rule()
    cands = {"WP1.1": ("rule", FROZEN["floor"], FROZEN["cap"]), "WP1.0": ("rule", 0.0, FROZEN["cap"])}
    per = run_seeds(seeds, {"rule": rule}, cands)
    summ = summarize(per, seeds, ["pay_all", "edits_tuned", "hand_rule_c1", "WP1.0", "WP1.1"])
    w = np.array([per[s]["WP1.1"]["score"] for s in seeds]); e = np.array([per[s]["edits_tuned"]["score"] for s in seeds])
    t = stats.ttest_rel(w, e)
    cells = summ["WP1.1"]["cell_gains_sum"]
    primary = {"mean_gain_per_seed": round(float((w - e).mean())), "p_one_sided": float(t.pvalue / 2 if t.statistic > 0 else 1 - t.pvalue / 2), "seeds_better": int((w > e).sum()),
               "all_nine_cells_positive": all(v > 0 for v in cells.values()), "worst_cell_gain_per_seed": round(min(cells.values()) / len(seeds))}
    primary["pass"] = bool(primary["mean_gain_per_seed"] >= 3000 and primary["p_one_sided"] < 0.05 and primary["all_nine_cells_positive"])
    os.makedirs(OUT, exist_ok=True)
    json.dump({"seeds": seeds, "frozen": FROZEN, "summary": summ, "primary": primary, "per_seed": per}, open(os.path.join(OUT, tag + ".json"), "w"), indent=1)
    print(json.dumps({"summary": {k: {kk: v[kk] for kk in ("sum", "median", "above_zero", "largest_seed_share", "worst_cell_gain_per_seed")} for k, v in summ.items()}, "primary": primary}, indent=1))
    if record:
        reg.record_use("4.2", pool, arm, "confirm", seeds, reference, "frozen WP1.1 read once against the tuned edit", "2026-10-23")


if __name__ == "__main__":
    if sys.argv[1] == "confirm":
        read(CONF, "confirm", "P-DEV2", "WP1.1-confirm", "--record" in sys.argv, "docs/wp11_confirm.md")
    if sys.argv[1] == "final":
        read(FINAL, "final_dev", "P-DEV2", "WP1.1-final-dev", "--record" in sys.argv, "docs/wp11_final_dev.md")
    if sys.argv[1] == "loop":
        loop()
