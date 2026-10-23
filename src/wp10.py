"""Workflow WP1.0 (prepay point 4, API-free): code fixes the order. A provider prior (the screen eb_upper_t, refreshed as claims arrive), a learned rule that
estimates what pending each claim is worth, a daily pend cap, then rules on the returned chart (src/prepay_env.resolve_pend).

For each receipt day, the claims received that day are scored from payer-visible fields and the history before them; the best `cap` claims whose estimated value is above
`floor` are pended; the rest are paid as billed. A pended claim is resolved by the office's answer: pay the level the chart supports (never above billed); no record is a denial;
no usable answer by the wait limit follows the arm's expired policy.

Nothing here reads the answer key or imports eval/. The training label is what pending a claim returned in the office (the chart's level, NO_RECORD, or no answer), valued with the
arm's own copy of the P1.0 cost parameters (a test requires the copies to equal eval/score_prepay.PARAMS). Easier by construction: the chart is in hand before payment, so a pend that
returns a chart is resolved exactly; the generator plants the test-line covariate of the prior and the impossible-day pattern the pile-on features pick up.
"""
import math
from collections import defaultdict
from datetime import timedelta

import numpy as np

from claim_stream import EM_CODES
from prepay_env import WAIT_LIMIT, level, resolve_pend, resolve_response

HOURS, BENEFIT = 2080, 1.4
WAGE = {"analyst": 78000, "coder": 51140, "admin": 45930}
COSTS = {"triage_min": 5, "admin_min": 10, "review_min": 15, "followup_min": 10, "appeal_min": 45, "copy_fee": 3.0,
         "wrongful_pend": 43.84, "wrongful_adjust": 200.0, "p_appeal": 0.5, "prompt_pay_days": 30, "interest": 0.18}
FEATURES = ("log_prior", "level", "has_test", "n_dx", "n_today_clinician", "n_today_group", "hist_n", "hist_hi_shrunk", "member_30", "lag")
SHRINK_N = 20
CAP_PER_DAY = 10


def _hourly(role):
    return WAGE[role] * BENEFIT / HOURS


def pend_value(stream, claim, d, payable_hat, over_hat):
    """The arm's belief of the net dollars of pending `claim` (decision `d`) against paying it as billed, given a belief about what the visit supports: the same arithmetic as P1.0's
    claim_value, with the believed payable standing in for the truth. Used for training labels and for nothing else."""
    P = COSTS
    paid = 0.0 if d.paid_cpt is None else stream.paid_at(claim, d.paid_cpt)
    v = claim.paid - paid                                                      # prevented
    v -= max(0.0, payable_hat - paid)                                         # money owed and not paid
    v -= P["triage_min"] / 60 * _hourly("analyst") + P["admin_min"] / 60 * _hourly("admin")
    v -= d.charts * (P["review_min"] / 60 * _hourly("coder") + P["copy_fee"])
    v -= max(0, d.rounds - 1) * (P["followup_min"] / 60 * _hourly("admin") + P["copy_fee"])
    w = 0.0 if over_hat else 1.0
    v -= w * P["wrongful_pend"] * d.rounds
    v -= w * paid * P["interest"] * max(0, d.days_to_pay - P["prompt_pay_days"]) / 365
    if paid < payable_hat - 0.005:
        v -= P["p_appeal"] * P["wrongful_adjust"] + P["p_appeal"] * P["appeal_min"] / 60 * _hourly("coder")
    return v


def proxy_payable(stream, claim, response):
    """What a coder's reading of the returned chart says the visit supports: (payable_hat, over_hat). No usable answer is treated as honest (nothing was shown)."""
    if response.no_record:
        return 0.0, True
    if response.chart_cpt is not None and response.day is not None and response.day <= WAIT_LIMIT:
        lvl = min(level(response.chart_cpt), level(claim.billed_cpt))
        return min(claim.paid, stream.paid_at(claim, EM_CODES[lvl])), lvl < level(claim.billed_cpt)
    return claim.paid, False


def claim_features(stream, prior):
    """(X, claims): one row of FEATURES per claim in stream order. Causal: row i uses claims received before claim i and the prior's snapshot in force on its receipt date."""
    n = len(stream.claims)
    X = np.zeros((n, len(FEATURES)))
    today_c, today_g = defaultdict(int), defaultdict(int)
    hist_n, hist_hi = defaultdict(int), defaultdict(int)
    by_pm = defaultdict(list)
    tot = hi = 0
    for i, c in enumerate(stream.claims):
        who = c.rendering if c.rendering is not None else c.provider
        glob = hi / tot if tot else 0.5
        h_n, h_hi = hist_n[who], hist_hi[who]
        recent = sum(1 for d in by_pm[(who, c.member)] if timedelta(0) <= c.service_date - d <= timedelta(days=30))
        X[i] = (math.log(max(prior.prior(c), 1e-6)), level(c.billed_cpt), 1.0 if c.has_test else 0.0, len(c.dx),
                today_c[(who, c.service_date)], today_g[(c.provider, c.service_date)], h_n, (h_hi + SHRINK_N * glob) / (h_n + SHRINK_N), recent,
                (c.receipt_date - c.service_date).days)
        today_c[(who, c.service_date)] += 1
        today_g[(c.provider, c.service_date)] += 1
        hist_n[who] += 1
        is_hi = c.billed_cpt in ("99214", "99215")
        hist_hi[who] += is_hi
        by_pm[(who, c.member)].append(c.service_date)
        tot += 1
        hi += is_hi
    return X


def is_resolved(response):
    """The pend returned something a coder can read: a chart inside the wait limit, or NO_RECORD. Anything else (no answer, a deficient chart never fixed) says nothing about the visit."""
    return bool(response.no_record or (response.chart_cpt is not None and response.day is not None and response.day <= WAIT_LIMIT))


def training_labels(stream, office, expired_policy="deny"):
    """(value, resolved): the value of pending each claim from the office's answers only, in stream order, and whether the pend was resolved. The office is deterministic per
    claim, so this is what a payer that had pended every claim in a past period would have seen. Training uses resolved rows only: for an unresolved pend the payer learns
    nothing about the visit, and valuing it as honest (or as upcoded) teaches the rule the valuer's assumption rather than the claim (hypothesis H7, docs/wp10_loop.md)."""
    v = np.zeros(len(stream.claims))
    ok = np.zeros(len(stream.claims), dtype=bool)
    for i, c in enumerate(stream.claims):
        r = office.request(c)
        d = resolve_response(stream, c, r, expired_policy=expired_policy)
        payable_hat, over_hat = proxy_payable(stream, c, r)
        v[i] = pend_value(stream, c, d, payable_hat, over_hat)
        ok[i] = is_resolved(r)
    return v, ok


def days_index(stream):
    """Group stream positions by receipt date: [(date, [positions])] in order."""
    out, last = [], None
    for i, c in enumerate(stream.claims):
        if c.receipt_date != last:
            out.append((c.receipt_date, []))
            last = c.receipt_date
        out[-1][1].append(i)
    return out


def pick(stream, score, cap=CAP_PER_DAY, floor=0.0, eligible=None):
    """Positions to pend: per receipt day, the top `cap` by score among eligible claims whose score is above `floor`. Day-batched: day d's choices use claims through day d."""
    chosen = []
    for _, pos in days_index(stream):
        cand = [i for i in pos if score[i] > floor and (eligible is None or eligible[i])]
        cand.sort(key=lambda i: -score[i])
        chosen.extend(cand[:cap])
    return chosen


def decisions(stream, office, chosen, expired_policy="deny"):
    return [resolve_pend(stream, office, stream.claims[i], expired_policy=expired_policy) for i in chosen]


class Rule:
    """The learned pend-or-pay rule: gradient-boosted trees regressing the pend value (dollars) on FEATURES."""

    def __init__(self, features=FEATURES, **kw):
        from sklearn.ensemble import HistGradientBoostingRegressor
        self.cols = [FEATURES.index(f) for f in features]
        self.model = HistGradientBoostingRegressor(**{"max_depth": 4, "max_iter": 150, "learning_rate": 0.1, "random_state": 0, **kw})

    def fit(self, X, v):
        self.model.fit(X[:, self.cols], v)
        return self

    def predict(self, X):
        return self.model.predict(X[:, self.cols])


def train(parts, features=FEATURES, expired_policy="deny", **kw):
    """Fit the rule on past periods: `parts` is a list of (stream, office, prior). Resolved pends only."""
    Xs, vs = [], []
    for stream, office, prior in parts:
        X = claim_features(stream, prior)
        v, ok = training_labels(stream, office, expired_policy)
        Xs.append(X[ok])
        vs.append(v[ok])
    return Rule(features, **kw).fit(np.vstack(Xs), np.concatenate(vs))


def run(stream, office, prior, rule, cap=CAP_PER_DAY, floor=0.0, expired_policy="deny"):
    """WP1.0 end to end on one stream: the Decisions for the claims it pends (every other claim is paid as billed)."""
    X = claim_features(stream, prior)
    chosen = pick(stream, rule.predict(X), cap, floor)
    return decisions(stream, office, chosen, expired_policy)
