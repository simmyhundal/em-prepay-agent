"""The oracle with triage: reads the answer key, pends exactly the claims whose prevented dollars exceed what pending them costs, and resolves each
through the real office (delays, unavailable charts, noisy reads). An upper bound, not an arm. Uses the same costs a tuned arm pays."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import score_prepay as sp
from prepay_env import resolve_pend


def run(stream, office, truth, params=sp.PARAMS):
    """Pend a claim only when the resolved pend adds to the score (the oracle sees how the office will answer, so it skips pends that would end in a wrongful denial)."""
    out = []
    for c in stream:
        t = truth[c.claim_id]
        if not t["overbilled"]:
            continue
        d = resolve_pend(stream, office, c)
        v0, v1 = sp.claim_value(stream, c, t, None, params), sp.claim_value(stream, c, t, d, params)
        net = lambda v: v["prevented"] - v["wrongful_loss"] - v["staff"] - v["abrasion"]
        if net(v1) > net(v0):
            out.append(d)
    return out
