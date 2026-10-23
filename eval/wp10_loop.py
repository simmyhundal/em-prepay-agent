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


def fit_rule(seeds, label="proxy_deny", features=wp10.FEATURES, **kw):
    X = np.vstack([we.table(s)["X"] for s in seeds])
    v = np.concatenate([we.table(s)[label] for s in seeds])
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


if __name__ == "__main__":
    if sys.argv[1] == "controls":
        r = controls()
        for k, v in r.items():
            print(k, round(v.sum()), [round(x) for x in v])
