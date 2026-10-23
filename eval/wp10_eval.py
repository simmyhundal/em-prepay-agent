"""Evaluation support for WP1.0 (eval side: reads the answer key). Per seed it builds a table of what pending EACH claim would be worth under P1.0 with the true answer
(`true_deny`, `true_pay`: expired pends denied, or paid as billed), beside the arm's own training label from the office alone (`proxy_deny`, `proxy_pay`) and the arm's
features. An arm that pends a set of claims scores  sum(true value of its pends) - the automatic-screen cost;  `score_set` does that arithmetic and `verify` checks it
against eval/score_prepay.score on the real decisions. The table is a cache (data/pp_<seed>/wp10_table_v1.npz); the arm modules never read it."""
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import claim_stream as cs
import provider_prior
import score_prepay as sp
import wp10
from prepay_env import resolve_response
from run_prepay_reference import build

TABLE_VERSION = 1


def net(v):
    return v["prevented"] - v["wrongful_loss"] - v["staff"] - v["abrasion"]


def table(seed, rebuild=False):
    d, key = build(seed)
    path = os.path.join(d, f"wp10_table_v{TABLE_VERSION}.npz")
    if os.path.exists(path) and not rebuild:
        z = np.load(path)
        return {k: z[k] for k in z.files}
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    prior = provider_prior.CausalPrior(stream)
    X = wp10.claim_features(stream, prior)
    n = len(stream.claims)
    out = {k: np.zeros(n) for k in ("proxy_deny", "proxy_pay", "true_deny", "true_pay", "paid", "resp_day", "resp_chart", "resp_norecord", "over", "kind")}
    for i, c in enumerate(stream.claims):
        r = office.request(c)
        t = truth[c.claim_id]
        for pol in ("deny", "pay"):
            dec = resolve_response(stream, c, r, expired_policy="pay_billed" if pol == "pay" else "deny")
            ph, oh = wp10.proxy_payable(stream, c, r)
            out["proxy_" + pol][i] = wp10.pend_value(stream, c, dec, ph, oh)
            out["true_" + pol][i] = net(sp.claim_value(stream, c, t, dec))
        out["paid"][i] = c.paid
        out["resp_day"][i] = -1 if r.day is None else r.day
        out["resp_chart"][i] = -1 if r.chart_cpt is None else cs.EM_CODES.index(r.chart_cpt)
        out["resp_norecord"][i] = r.no_record
        out["over"][i] = t["overbilled"]
        out["kind"][i] = {None: 0, "not_rendered": 1, "impossible_days": 2}.get(t["kind"], 3)
    day = np.array([(c.receipt_date - stream.claims[0].receipt_date).days for c in stream.claims])
    out.update({"X": X, "day": day, "level": X[:, wp10.FEATURES.index("level")]})
    np.savez(path, **out)
    return out


def score_set(tab, chosen, policy="deny"):
    """Net P1.0 score of an arm that pends the positions in `chosen` and pays the rest as billed."""
    chosen = np.asarray(chosen, dtype=int)
    return float(tab["true_" + policy][chosen].sum() - sp.PARAMS["auto_screen"] * len(tab["day"]))


def verify(seed, chosen, policy="deny"):
    """The table's arithmetic equals the real score on the real decisions (run once per change to either side)."""
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    dec = wp10.decisions(stream, office, chosen, "pay_billed" if policy == "pay" else "deny")
    return sp.score(stream, truth, dec)["score"], score_set(table(seed), chosen, policy)


if __name__ == "__main__":
    import multiprocessing as mp
    seeds = [int(s) for s in sys.argv[1:]]
    with mp.get_context("spawn").Pool(8) as p:
        print(p.map(table, seeds))
