"""Prepay point 3: claim edits at adjudication. Rules on the claim and the provider's history before it; no chart is requested.
A claim that trips an edit is denied; the provider can appeal (the score charges that). The defaults are first guesses, not tuned; tuned values are chosen on development seeds and reported in docs/prepay_reference_arms.md."""
from collections import defaultdict
from datetime import timedelta

from score_prepay_decision import Decision

DAILY_MAX = 30        # E/M claims by one billing group for one service date
MEMBER_MAX = 4        # E/M claims by one provider for one member within 30 days before the service date


def run(stream, daily_max=DAILY_MAX, member_max=MEMBER_MAX, by="provider"):
    per_day = defaultdict(int)
    by_pm = defaultdict(list)
    out = []
    for c in stream:                                   # receipt order: state holds only claims received so far
        who = c.provider if by == "provider" else c.rendering     # billing group (the default) or rendering clinician
        key = (who, c.service_date)
        per_day[key] += 1
        recent = sum(1 for d in by_pm[(who, c.member)] if timedelta(0) <= c.service_date - d <= timedelta(days=30))
        by_pm[(who, c.member)].append(c.service_date)
        if per_day[key] > daily_max or recent >= member_max:
            out.append(Decision(c.claim_id, "adjust", None, 0, 0, 0))
    return out
