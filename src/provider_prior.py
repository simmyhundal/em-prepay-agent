"""The provider prior of workflow WP1.0: the postpay screen eb_upper_t (src/screen_methods_v4.py in the pinned generator checkout), recomputed as claims arrive.

eb_upper_t is the empirical-Bayes shrunk ratio of observed to expected visits billed 99214 or 99215 per clinician, with the member's chronic-condition count and the
lab or test line as covariates. The postpay screen runs once on a finished year. Here it is refreshed every `refresh_days` days of receipt dates from the claims received
BEFORE the refresh date only (diagnoses and levels), so no decision sees a later claim. Before `min_claims` claims have arrived the prior is 1.0 for everyone (cold start).
Payer-visible fields only; nothing here reads the answer key or the records.

Easier by construction: the generator draws a visit's lab line from the true complexity, so the test-line covariate is planted (see the screen_methods_v4 docstring).
"""
import os
import pickle
import sys
from datetime import timedelta

import numpy as np

import claim_stream as cs

VERSION = 1
REFRESH_DAYS = 7
MIN_CLAIMS = 3000
LEVELS = list(cs.EM_CODES)


def _modules():
    cs._gen()
    import baseline_riskadj as ra
    import derive
    import screen_methods as sm
    return sm, ra, derive


def scores_from(sm, ra, derive, prov, level, member_codes, members, test):
    """eb_upper_t on the given rows. `member_codes[m]` is the set of condition codes seen for member m so far."""
    cnt = np.array([min(len(member_codes.get(m, ())), sm.MAX_COUNT) for m in members])
    D = {"prov": prov, "level": level}
    X = np.hstack([sm.design_count(cnt), test[:, None]])
    _, sc = sm._binary_fit(D, X, min_level=3)
    return sm.eb_scores(sc)["eb_ratio"]


class CausalPrior:
    """prior(claim) -> the score of the claim's clinician at the latest refresh on or before the claim's receipt date. Build once per stream, then query in any order."""

    def __init__(self, stream, refresh_days=REFRESH_DAYS, min_claims=MIN_CLAIMS, cache=True):
        self.stream = stream
        path = os.path.join(stream.data_dir, f"prior_cache_v{VERSION}_{refresh_days}_{min_claims}.pkl")
        if cache and os.path.exists(path):
            self.snapshots = pickle.load(open(path, "rb"))
        else:
            self.snapshots = self._build(refresh_days, min_claims)
            if cache:
                pickle.dump(self.snapshots, open(path, "wb"))
        self.dates = sorted(self.snapshots)

    def _build(self, refresh_days, min_claims):
        sm, ra, derive = _modules()
        claims = [c for c in self.stream.claims if c.rendering is not None]
        codes = set(derive.CONDITION_MAP)
        member_codes, i, n = {}, 0, len(claims)
        prov, level, member, test = [], [], [], []
        snaps, d = {}, claims[0].receipt_date + timedelta(days=refresh_days)
        while i < n:
            if claims[i].receipt_date >= d:               # a refresh uses only claims received strictly before d
                if len(prov) >= min_claims:
                    snaps[d] = scores_from(sm, ra, derive, np.array(prov), np.array(level), member_codes, member, np.array(test, dtype=float))
                d += timedelta(days=refresh_days)
                continue
            c = claims[i]
            prov.append(c.rendering)
            level.append(LEVELS.index(c.billed_cpt))
            member.append(c.member)
            test.append(1.0 if c.has_test else 0.0)
            s = member_codes.setdefault(c.member, set())
            s.update(x for x in c.dx if x in codes)
            i += 1
        return snaps

    def at(self, receipt_date):
        """The snapshot in force on a date: {clinician: score} or {} in the cold start."""
        best = None
        for d in self.dates:
            if d <= receipt_date:
                best = d
            else:
                break
        return self.snapshots[best] if best else {}

    def prior(self, claim):
        return self.at(claim.receipt_date).get(claim.rendering, 1.0)
