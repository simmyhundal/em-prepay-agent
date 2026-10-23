"""Resolving a pend: what an arm pays once the office has answered (or has not by the wait limit). Shared by every arm."""
from claim_stream import EM_CODES
from score_prepay_decision import Decision

WAIT_LIMIT = 45              # days; assumption, Medicare ADR's 45 days (docs/score_prepay.md)
EXPIRED_POLICY = "deny"      # "deny" or "pay_billed"


def level(cpt):
    return EM_CODES.index(cpt)


def resolve_pend(stream, office, claim, expired_policy=EXPIRED_POLICY, wait_limit=WAIT_LIMIT):
    """Request the chart for `claim`; pay at most the billed level, at the level the chart supports. No usable chart by the wait limit (or a
    claim never rendered): the expired policy decides. Returns a Decision."""
    return resolve_response(stream, claim, office.request(claim), expired_policy, wait_limit)


def resolve_response(stream, claim, r, expired_policy=EXPIRED_POLICY, wait_limit=WAIT_LIMIT):
    """The same resolution from a response already in hand (the office is deterministic per claim, so callers may cache the request)."""
    if r.chart_cpt is not None and r.day is not None and r.day <= wait_limit:
        lvl = min(level(r.chart_cpt), level(claim.billed_cpt))
        return Decision(claim.claim_id, "pend", EM_CODES[lvl], r.day, r.rounds, 1)
    paid = claim.billed_cpt if expired_policy == "pay_billed" else None
    return Decision(claim.claim_id, "pend", paid, wait_limit, r.rounds, 0)
