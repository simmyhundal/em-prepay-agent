"""Prepay point 6: automatic level adjustment without records (the Cigna and Aetna approach, docs/market_research_earnings.md in the postpay repository).
A claim billed 99214 or 99215 is paid one level lower. Variants: `run_all` adjusts every such claim; `run_provider` only those of a provider whose share of
level 4 and 5 visits among its earlier claims exceeds the peers' share (all providers' earlier claims) by `delta`, with at least `min_n` earlier claims.
The provider can appeal a wrongful adjustment; the score charges that."""
from claim_stream import EM_CODES
from score_prepay_decision import Decision

HIGH = ("99214", "99215")


def _down(cpt):
    return EM_CODES[EM_CODES.index(cpt) - 1]


def run_all(stream):
    return [Decision(c.claim_id, "adjust", _down(c.billed_cpt), 0, 0, 0) for c in stream if c.billed_cpt in HIGH]


def run_provider(stream, delta=0.2, min_n=20):
    tot = hi = 0
    pt, ph = {}, {}
    out = []
    for c in stream:
        n, h = pt.get(c.provider, 0), ph.get(c.provider, 0)
        if c.billed_cpt in HIGH and n >= min_n and tot >= 200 and h / n > hi / tot + delta:
            out.append(Decision(c.claim_id, "adjust", _down(c.billed_cpt), 0, 0, 0))
        pt[c.provider] = n + 1
        ph[c.provider] = h + (c.billed_cpt in HIGH)
        tot += 1
        hi += c.billed_cpt in HIGH
    return out
