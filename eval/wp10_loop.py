"""The WP1.0 hypothesis loop on P-DEV (fit j = 30 to 39, select j = 40 to 49). Free. Every hypothesis is one change against the current best, scored on the select seeds with
the cached tables (eval/wp10_eval.py), compared paired per seed, with a same-cap control. The ledger (experiments/wp10/ledger.json) counts hypotheses for the Bonferroni bar.
Usage: python eval/wp10_loop.py controls | h <name>"""
import json
import os
import sys

import numpy as np
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import claim_stream as cs
import wp10
import wp10_eval as we
import seed_registry as reg
from run_prepay_reference import DEV

FIT, SEL = DEV[30:40], DEV[40:50]
CAP = wp10.CAP_PER_DAY
LEDGER = os.path.join(ROOT, "experiments", "wp10", "ledger.json")
SCREEN = 0.05


class Days:
    """Receipt-day groups for a table (positions), without rebuilding a stream."""
    def __init__(self, tab):
        day = tab["day"]
        self.groups = np.split(np.arange(len(day)), np.flatnonzero(np.diff(day)) + 1)


def pick(tab, days, score, cap=CAP, floor=-np.inf, eligible=None):
    out = []
    for g in days.groups:
        s = score[g]
        ok = s > floor
        if eligible is not None:
            ok &= eligible[g]
        idx = g[ok]
        if len(idx):
            out.extend(idx[np.argsort(-score[idx], kind="stable")[:cap]])
    return np.array(out, dtype=int)


def load(seeds):
    return {s: (we.table(s), None) for s in seeds}


def resolved(tab):
    return (tab["resp_norecord"] == 1) | ((tab["resp_chart"] >= 0) & (tab["resp_day"] >= 0) & (tab["resp_day"] <= wp10.WAIT_LIMIT))


def fit_rule(seeds, label="proxy_deny", features=wp10.FEATURES, drop_unresolved=True, **kw):
    ts = [we.table(s) for s in seeds]
    k = [resolved(t) if drop_unresolved else np.ones(len(t["day"]), bool) for t in ts]
    X = np.vstack([t["X"][m] for t, m in zip(ts, k)])
    v = np.concatenate([t[label][m] for t, m in zip(ts, k)])
    return wp10.Rule(features, **kw).fit(X, v)


def run_arm(seeds, chooser, policy="deny"):
    """chooser(tab, days) -> positions pended. Returns per-seed net score."""
    out = []
    for s in seeds:
        tab = we.table(s)
        ch = chooser(tab, Days(tab))
        out.append(we.score_set(tab, ch, policy))
    return np.array(out)


def summarize(name, v, ref=None, ref_name=None):
    row = {"arm": name, "sum": round(float(v.sum())), "median": round(float(np.median(v))), "above_zero": int((v > 0).sum()), "per_seed": [round(float(x)) for x in v]}
    if ref is not None:
        d = v - ref
        row.update({"vs": ref_name, "diff_sum": round(float(d.sum())), "diff_mean": round(float(d.mean())), "p_t": float(stats.ttest_rel(v, ref).pvalue),
                    "p_wilcoxon": float(stats.wilcoxon(d).pvalue) if np.any(d != 0) else 1.0, "seeds_better": int((d > 0).sum())})
    return row


def controls(seeds=SEL, cap=CAP):
    rng = np.random.RandomState(0)
    hi = lambda t: t["level"] >= 3
    res = {}
    res["pay_all"] = np.zeros(len(seeds))
    res["screen_only"] = np.full(len(seeds), 0.0) - np.array([SCREEN * len(we.table(s)["day"]) for s in seeds])
    res["random_cap"] = run_arm(seeds, lambda t, d: pick(t, d, rng.rand(len(t["day"])), cap, eligible=hi(t)))
    res["prior_cap"] = run_arm(seeds, lambda t, d: pick(t, d, t["X"][:, 0], cap, eligible=hi(t)))
    res["oracle_cap"] = run_arm(seeds, lambda t, d: pick(t, d, t["true_deny"], cap, floor=0.0))
    return res


def edits_tuned(seeds):
    """The tuned claim edit (docs/prepay_reference_arms.md) on the same seeds: the competitor that needs no chart."""
    import edit_rules
    import score_prepay as sp
    out = []
    for s in seeds:
        d, key = we.build(s)
        st = cs.Stream(d, seed=s)
        out.append(sp.score(st, sp.claim_truth(key, st), edit_rules.run(st, by="rendering", daily_max=20, member_max=6))["score"])
    return np.array(out)


def report(seeds=SEL):
    """Hypotheses H1 to H8 and the controls on the select seeds. Prints a table and writes experiments/wp10/ledger.json."""
    F = wp10.FEATURES
    noprior = [f for f in F if f != "log_prior"]
    def learned(feats, drop=True, label="proxy_deny", pol="deny", cap=CAP, floor=0.0):
        r = fit_rule(FIT, label, feats, drop_unresolved=drop)
        ns = []
        def ch(t, d):
            c = pick(t, d, r.predict(t["X"]), cap, floor)
            ns.append(len(c))
            return c
        return run_arm(seeds, ch, pol), sum(ns)
    rows, arms = {}, {}
    arms["H1 learned rule, all rows (unresolved valued as honest)"] = learned(F, drop=False)
    arms["H2 H1 with expired pends paid as billed"] = learned(F, drop=False, label="proxy_pay", pol="pay")
    arms["H3 H1 without the prior"] = learned(noprior, drop=False)
    arms["H4 H1 on pile-on features only"] = learned(["n_today_clinician", "n_today_group", "level"], drop=False)
    arms["H7 train on resolved pends only (WP1.0 candidate)"] = learned(F)
    arms["H8 H7 without the prior (ablation)"] = learned(noprior)
    arms["H9 H7 with cap 5"] = learned(F, cap=5)
    arms["H10 H7 with cap 30"] = learned(F, cap=30)
    j = wp10.FEATURES.index("n_today_clinician")
    arms["C1 hand rule: pend when the clinician already has 20 claims that service date"] = (run_arm(seeds, lambda t, d: pick(t, d, t["X"][:, j], CAP, 19.5)), None)
    best = arms["H7 train on resolved pends only (WP1.0 candidate)"]
    n = best[1]
    rng = np.random.RandomState(3)
    per = max(1, n // len(seeds))
    arms["C2 random pends, same count as H7 (billed 99214 or 99215)"] = (run_arm(seeds, lambda t, d: rng.choice(np.flatnonzero(t["level"] >= 3), per, replace=False)), None)
    arms["C3 prior only, top 10 per day among 99214 and 99215"] = (run_arm(seeds, lambda t, d: pick(t, d, t["X"][:, 0], CAP, eligible=t["level"] >= 3)), None)
    arms["C4 tuned claim edit (denies, no chart)"] = (edits_tuned(seeds), None)
    arms["C5 oracle at 10 pends a day (answer key)"] = (run_arm(seeds, lambda t, d: pick(t, d, t["true_deny"], CAP, 0.0)), None)
    arms["C6 screen only (pays everything, charged the screen)"] = (np.full(len(seeds), 0.0) - np.array([SCREEN * len(we.table(s)["day"]) for s in seeds]), None)
    out = {"seeds": seeds, "rows": []}
    for k, (v, np_) in arms.items():
        r = summarize(k, v, best[0], "H7")
        r["pends"] = np_
        out["rows"].append(r)
        print(f"{k:90s} sum {r['sum']:>9} median {r['median']:>7} >0 {r['above_zero']:>2}" + (f"  vs H7 {r.get('diff_sum'):>9} p_t {r.get('p_t'):.3g}" if "diff_sum" in r else ""))
    out["hypotheses_counted"] = {"changes": 10, "settings_scored_on_select": 59,
                                 "note": "H1 to H10 are changes; about 59 settings (cap and floor grids, threshold rules, classifier thresholds) were also scored on the select seeds"}
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    json.dump(out, open(LEDGER, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "report":
        report()
        sys.exit()
    if sys.argv[1] == "controls":
        r = controls()
        for k, v in r.items():
            print(k, round(v.sum()), [round(x) for x in v])
